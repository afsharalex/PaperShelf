"""
Main entry point for the PaperShelf application.

This module provides a convenient way to start the PaperShelf API server.
"""

import uvicorn

from papershelf.api.app import create_app
from papershelf.utils.config import config


def main():
    """Run the PaperShelf API server."""
    app = create_app()
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()