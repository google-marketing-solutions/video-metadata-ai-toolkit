#!/bin/bash

set -e

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

pip3 install -q -r requirements.txt

printf "Tests:\n"
python3 -m unittest discover "video_metadata_toolkit" -p "*_test.py"
printf "\nLint:"
pylint video_metadata_toolkit