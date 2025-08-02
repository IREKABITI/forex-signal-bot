#!/bin/bash

echo "Installing requests and matplotlib..."
pip install --upgrade pip
pip install requests matplotlib

echo "Starting bot..."
python main.py
