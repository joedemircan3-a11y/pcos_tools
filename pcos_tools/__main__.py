"""Allow ``python -m pcos_tools <command>``."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
