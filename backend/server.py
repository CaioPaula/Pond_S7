from modules import *
from serial.tools import list_ports
from flask import Flask, request, render_template, redirect, jsonify
from tinydb import TinyDB, Query
import datetime

server = Flask(__name__)

# Initialize TinyDB databases
logs = TinyDB('../db/logs.json')
positions = TinyDB('../db/positions.json')

# Global variable to store the bot instance
bot = None

def log_request():
    # Function to log HTTP requests
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    request_data = {
        'timestamp': current_time,
        'method': request.method,
        'path': request.path,
        'query_string': request.query_string.decode('utf-8'),
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string
    }
    logs.insert(request_data)

@server.before_request
def before_request():
    # Log HTTP requests before processing
    log_request()

@server.route("/")
def index():
    # Render the index.html template
    return render_template("index.html")


@server.route("/check_bot_status")
def check_bot_status():
    try:
        if bot and bot.status:
            if bot.status == "Connected":
                return """<span class="nav-link active" id="bot_status_text">Bot Status: </span>
                          <p class="center text-success" id="bot_status_value">Connected</p>"""
            elif bot.status == "Disconnected":
                return """<span class="nav-link active" id="bot_status_text">Bot Status: </span>
                          <p class="center text-danger" id="bot_status_value">Disconnected</p>"""
            else:
                return """<span class="nav-link active" id="bot_status_text">Bot Status: </span>
                          <p class="center" id="bot_status_value">Unknown</p>"""
        else:
            return """<span class="nav-link active" id="bot_status_text">Bot Status: </span>
                      <p class="center" id="bot_status_value">Bot not available</p>"""
    except Exception as e:
        return f"Internal Server Error: {e}", 500  


@server.route("/connect_arm")
def connect_bot(): 
    # Route to connect the arm
    start_spiner("Connecting Arm...", 1.5)
    try:
        available_ports = list_ports.comports() 
        port = available_ports[0].device 
        global bot 
        bot = CaioBot(port, False)

        bot.status = "Connected"

        return redirect("/")
    except KeyError as e:
        return f'{e}'

@server.route("/disconnect_arm")
def disconnect_bot():
    # Route to disconnect the arm
    start_spiner("Disconnecting Arm...", 1.5)
    try:
        bot._disconnect()
    except Exception as e:
        fail_message(f"{e}", 1.5)
        connect_bot()
        bot._disconnect()
    
    bot.status = "Disconnected"

    return redirect("/")

@server.route("/move_home")
def move_home():
    # Route to move the arm to the home position
    start_spiner("Backing to home position...", 1)
    try:
        bot.home()
    except Exception as e:
        fail_message(f"{e}", 1.5)
        connect_bot()
        bot.home() 

    return redirect("/get_saved_positions")

@server.route("/get_position")
def get_position():
    # Route to get the current arm position
    start_spiner("Getting arm actual positions...", 1)
    try:
        x, y, z, r, j1, j2, j3, j4 = bot.pose()
        return f"Arm in --> X:{x} Y:{y} Z:{z} R:{r}"
    except:
        connect_bot()
        x, y, z, r, j1, j2, j3, j4 = bot.pose()
        return f"Arm in --> X:{x} Y:{y} Z:{z} R:{r}"

@server.route("/move_to", methods=["POST"])
def move_l_to():
    # Route to move the arm to a specified position
    start_spiner("Moving to position...", 1.5)
    x = float(request.form["x"])
    y = float(request.form["y"])
    z = float(request.form["z"])
    r = float(request.form["r"])
    print(x , y, z, r)

    try:
        bot._move_l(x, y, z, r)
    except Exception as e:
        fail_message(f"{e}", 1.5)
        connect_bot()
        bot._move_l(x, y, z, r)

    return redirect("/")

@server.route("/save_position", methods=["POST"])
def save_position():
    # Route to save a position
    position_name = request.form["position-name"]
    try:
        x, y, z, r, j1, j2, j3, j4 = bot.pose()
    except:
        connect_bot()
        x, y, z, r, j1, j2, j3, j4 = bot.pose()

    position_data = {
        "name" : position_name,
        'x': x,
        'y': y,
        'z': z,
        'r': r
    }

    positions.insert(position_data)

    return redirect("/get_saved_positions")

@server.route("/get_saved_positions", methods=["GET", "POST"])
def get_saved_positions():
    # Route to get saved positions
    positions_list = positions.all()
    return render_template("positions.html", positions=positions_list)

@server.route("/move_to_saved_position/<string:position_name>", methods=["POST"])
def move_to_saved_position(position_name):
    # Route to move to a saved position
    try:
        Position = Query()
        position = positions.get(Position.name == position_name)
        if position:
            x = position["x"]
            y = position["y"]
            z = position["z"]
            r = position["r"]
            
            # Move the arm to the specified position
            try:
                bot._move_l(x, y, z, r)
            except Exception as e:
                connect_bot()
                bot._move_l(x, y, z, r)
            
            return redirect("/get_saved_positions")

        else:
            return f"Position '{position_name}' not found.", 404
    except Exception as e:
        return f"Internal Server Error: {e}", 500

@server.route("/delete_saved_position/<string:position_name>", methods=["DELETE"])
def delete_saved_position(position_name):
    # Route to delete a saved position
    try:
        start_spiner("Deleting saved position...", 1.5)
        Position = Query()
        position = positions.get(Position.name == position_name)

        if position:
            position_id = position.doc_id
            positions.remove(doc_ids=[position_id])
            return redirect("/get_saved_positions")
        else:
            return f"Position '{position_name}' not found.", 404
    except Exception as e:
        return f"Internal Server Error: {e}", 500

@server.route("/get_logs")
def get_logs():
    # Route to get logs
    logs_list = logs.all()
    return render_template("logs.html", logs=logs_list)

@server.route("/clear_logs", methods=["GET"])
def clear_logs():
    # Route to clear logs
    print("banana")
    logs.truncate()  # Truncate the logs table, removing all data
    return redirect("/get_logs")

@server.route("/exit", methods=["POST"])
def exit_app():
    # Route to exit the application
    start_spiner("Exiting...", 1.5)
    try:
        bot.home()
        exit
    except Exception as e:
        fail_message(f"{e}", 1.5)
        connect_bot()
        bot.home()
        exit()


if __name__ == "__main__":
    server.run(debug=True)