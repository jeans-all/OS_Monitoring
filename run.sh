#!/bin/bash

# check if a virtual environment exists
check_venv(){
    if [[ -d "$1" &&  -f "$1/bin/activate" ]]; then 
        echo "Virtual environment '$1' found."
        return 0
    else
        echo "Virtual environment '$1' not found."
        return 1
    fi
}

# ask for virtual environment name
while true; do 
    read -p "Enter your virtual environment name: " venv_name

    if check_venv "$venv_name"; then 
        # from config.settings import ROOT_DIR cannot be resolved because it's a script that executes the streamlit. 
        export PYTHONPATH="${PYTHONPATH}:$(pwd)"
        source "$venv_name/bin/activate"
        break
    else
        read -p  "Virtual environment not found. Create one with this name? (y/n): " create_venv
        if [[ $create_venv =~ ^[Yy]$ ]]; then
            echo "Creating virtual environment '$venv_name'..."
            python3 -m venv "$venv_name"
            source "$venv_name/bin/activate"
            echo "Installing dependencies..."
            pip install -r requirements.txt
            break
        else
            echo "Failed to create virtual environment. Please check your Python installation."
        fi
    fi

done

if [ -z "$VIRTUAL_ENV" ]; then 
    echo "Failed to activate virtual environment. Exiting."
    exit 1
fi

echo "Virtual environment is active."

# run data collector as a background job
echo "Starting data collector..."
python3 src/data/collector.py &

# wait a moment for the collector to initialize
sleep 2

cd "$(dirname "$0")"

# run Streamlit application
streamlit run src/app/main.py


# deactivate virtual environment when the applciation is closed
deactivate

echo "Application cloesd. Thank you for using System Monitor Dashboard!"