#!/bin/bash

# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment and install dependencies
source venv/bin/activate && pip install -r requirements.txt && cd backend && python server.py
