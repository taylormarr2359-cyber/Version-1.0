"""Entry point for the ATLAS API server.

Usage:
    python -m projrvt.serve

Environment variables:
    ATLAS_API_HOST      Bind address (default: 0.0.0.0)
    ATLAS_API_PORT      Port (default: 8000)
    ATLAS_API_AUTH_KEY  Optional Bearer token for auth (default: disabled)
"""
import uvicorn

from .config import get_api_host, get_api_port


def main() -> None:
    host = get_api_host()
    port = get_api_port()
    print(f"ATLAS API starting on http://{host}:{port}")
    print(f"  PWA available at http://localhost:{port}/")
    print(f"  API docs at    http://localhost:{port}/docs")
    uvicorn.run("projrvt.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
