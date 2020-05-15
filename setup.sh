#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create virtualenv
ENV_DIR=${SCRIPT_DIR}/venv
python3 -m venv ${ENV_DIR}
source ${ENV_DIR}/bin/activate

# Install python dependencies
pip install -r "${SCRIPT_DIR}"/requirements.txt
