__version__ = "1.0.0"

# Load local environment variables from a .env file when available.
# This keeps secrets out of source control while allowing local dev convenience.
try:
	from dotenv import load_dotenv

	load_dotenv()
except Exception:
	# python-dotenv is optional; if not installed or .env is missing, proceed.
	pass

from .assistant import AtlasAssistant
from .main import run_cli

__all__ = ["AtlasAssistant", "run_cli", "__version__"]
