#!/bin/bash

# Validate registry bash entrypoint
# Runs python3 scripts/validate_packages.py and exits with the same code

python3 scripts/validate_packages.py
exit $?