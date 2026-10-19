import sys
from pathlib import Path

for parent in Path(__file__).parents:
    if (parent / 'movie_booking/__init__.py').is_file():
        sys.path.insert(0, str(parent))
        break
