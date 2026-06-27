#!/bin/bash

# Validate PR bash entrypoint
# Runs python3 scripts/validate_pr.py and passes GITHUB_BASE_REF if set
# Exits with the same code as the Python script

if [ -n "$GITHUB_BASE_REF" ]; then
    python3 scripts/validate_pr.py --base-ref "$GITHUB_BASE_REF"
else
    python3 scripts/validate_pr.py
fi

exit $?