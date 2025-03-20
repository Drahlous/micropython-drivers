#!/usr/bin/env bash

set -e

# Remove any existing venv and re-install
rm -rf .venv typings
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and micropython stubs
pip install -r requirements-dev.txt --target typings
