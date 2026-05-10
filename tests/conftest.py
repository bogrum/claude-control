import sys
from pathlib import Path

# Make `app` importable from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
