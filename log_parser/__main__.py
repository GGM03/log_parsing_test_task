#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Executable script for parsing log files
"""


import json
import sys
import os

from log_parser import parse_log_lines


def main():
    argv = sys.argv
    if len(argv) != 2:
        print('usage: log_parser <log file>')
        exit(-1)
    try:
        file_path = os.path.abspath(argv[1])
        with open(file_path, 'r') as file:
            # TODO: use "readline" and "parse_log_line" instead of "parse_log_lines"
            #  to prevent copying of huge log files in memory
            print(json.dumps(parse_log_lines(file.read()), indent=2))
    except (FileNotFoundError, PermissionError):
        print('Cant read file!')
        exit(-1)


if __name__ == '__main__':
    main()
