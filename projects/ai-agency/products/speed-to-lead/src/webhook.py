"""
Speed-to-Lead product webhook entry point.

Imports the core pipeline from the services layer so there is no code
duplication. All business logic lives in services/automation/speed_to_lead.py.

Run from the product root:
    python -m flask --app src/webhook run --port 5000

Or import the Flask app object directly:
    from src.webhook import app
"""

import sys
from pathlib import Path

# Add the services/automation directory to sys.path so the import resolves
# regardless of where the process is launched from.
_SERVICES_DIR = (
    Path(__file__).resolve().parents[3] / "services" / "automation"
)
if str(_SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICES_DIR))

from speed_to_lead import app, process_inquiry, load_client_config  # noqa: F401

__all__ = ["app", "process_inquiry", "load_client_config"]
