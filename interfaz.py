import os
import sys

# Ensure the parent and app directories are in Python's search path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from app.main import main

if __name__ == "__main__":
    main()