import os

# Function to get the type of operating system
def get_os_type() -> str:
    print(os.name)
    # Check if the OS is Windows
    if os.name == 'nt':
        return 'windows'
    # Check if the OS is Linux
    elif os.name == 'posix':
        return 'linux'
    # Check if the OS is macOS
    elif os.name == 'Darwin':
        return 'macos'
    # If the OS type is unknown
    else:
        return "?"

# Function to execute the program based on the operating system
def execute_program_on_os(os_type: str = get_os_type()) -> None:
    # Get the current directory path
    raw_current_dir_path = os.getcwd()
    current_dir_path = raw_current_dir_path.replace("\\", "/")

    # Use match statement to execute the appropriate batch file based on OS type
    match os_type:
        # For Windows
        case "windows":
            os.system(f"{current_dir_path}/bats/windows.bat")
        # For Linux
        case "linux":
            os.system(f"{current_dir_path}/bats/linux.bat")
        # For macOS
        case "macos":
            os.system(f"{current_dir_path}/bats/macos.bat")
        # For unknown OS type
        case "?":
            os.system(f"{current_dir_path}/bats/s.bat")

# Main entry point of the script
if __name__ == "__main__":
    # Execute the program based on the detected operating system
    execute_program_on_os()
