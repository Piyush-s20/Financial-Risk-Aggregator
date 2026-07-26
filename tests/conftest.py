import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for path in (ROOT / "backend", ROOT / "data_pipeline"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
