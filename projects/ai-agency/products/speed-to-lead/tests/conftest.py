"""
conftest.py -- inject services/automation into sys.path.

Module-level injection (not inside a hook) ensures paths are available
before pytest imports any test module in this directory.
"""

import sys
from pathlib import Path

_SERVICES_DIR = (
    Path(__file__).resolve().parents[3] / "services" / "automation"
)
_PRODUCT_SRC = Path(__file__).resolve().parents[1] / "src"

for _dir in [str(_SERVICES_DIR), str(_PRODUCT_SRC)]:
    if _dir not in sys.path:
        sys.path.insert(0, _dir)
