"""
Rebuild Database Script

WARNING: This will DROP all tables and recreate them from scratch.
All existing data will be lost. Do NOT run in production.

Usage:
    cd backend && .venv/bin/python scripts/database/rebuild_database.py
"""

import logging

from database import rebuild


logger = logging.getLogger(__name__)


def main():
    logger.info("Rebuilding database...")
    rebuild()
    logger.info("Database rebuild complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
