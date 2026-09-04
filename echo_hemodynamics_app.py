#!/usr/bin/env python3
"""
Entry point for echo_hemodynamics module.
Delegates to the CLI main function.
"""
import sys
from cli import main
if __name__ == '__main__':
    sys.exit(main())
