#!/bin/bash

# Create the virtual environment
python -m venv venv

# Activate the virtual environment and install dependencies
source venv/bin/activate && pip install -r requirements.txt && cd backend && python server.py