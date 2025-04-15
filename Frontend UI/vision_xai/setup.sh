#!/bin/bash

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed."
    echo "Please install Node.js from https://nodejs.org and re-run this script."
    exit 1
fi

# Run the Node.js script
echo "Node.js is installed. Running setup script..."
node setup.js
