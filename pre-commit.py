#! /bin/env python
"""Custom pre-commit script in order to ensure that each commited file is
pylint compliant"""

import re
import subprocess
import sys

from isort import isort


def nth_bit(num, nth):
    """Returns the nth bit"""
    return num & (1 << nth - 1)

# Get a list of the current files in the local tree
STATUS_OUT = subprocess.run(["git", "status", "-s", "-uno"], capture_output=True).stdout
FILES = STATUS_OUT.decode().split('\n')
# Get a list of the current staged files
STAGED_FILES_REGEXP = r"^A.*$"
STAGED_FILES = [
    # Get the filename
    # Since the output is like this `XX\s+ $filename` we need to split the
    # string and get the last element of the returned array
    staged_file.split(' ')[-1:][0]
    for staged_file in FILES
    if re.match(STAGED_FILES_REGEXP, staged_file)]

# Run isort and pylint on each file
# If one file fails, the script fails and returns 1
for staged_file in STAGED_FILES:
    isort.SortImports(staged_file)
    pylint_process = subprocess.run(["python", "-m", "pylint", staged_file])
    if pylint_process.returncode == 0:
        sys.exit(0)

    # If the return code is not zero, then each bit is checked to issue a
    # proper message to the user. The values are taken from
    # https://pylint.readthedocs.io/en/latest/user_guide/run.html#exit-codes
    if nth_bit(pylint_process.returncode, 1):
        print("pylint: fatal error")

    if nth_bit(pylint_process.returncode, 2):
        print("pylint: error")

    if nth_bit(pylint_process.returncode, 3):
        print("pylint: warning")

    if nth_bit(pylint_process.returncode, 4):
        print("pylint: code refactor needed")

    if nth_bit(pylint_process.returncode, 5):
        print("pylint: convention not followed")

    if nth_bit(pylint_process.returncode, 6):
        print("pylint: usage error")

    sys.exit(1)
