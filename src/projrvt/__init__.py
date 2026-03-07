__version__ = "1.0.0"

from .assistant import AtlasAssistant
from .main import run_cli

__all__ = ["AtlasAssistant", "run_cli", "__version__"]
