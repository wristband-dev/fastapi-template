"""
Safe Database Migration Script

This script ONLY creates tables if they don't exist.
It will NOT drop existing tables or modify existing data.
Safe to run in production.

Usage:
    cd backend && .venv/bin/python scripts/database/migrate_database.py
"""

import logging

from database import create_tables, setup_permissions, list_tables, test_connection


logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("SAFE DATABASE MIGRATION")
    logger.info("This will only CREATE tables if they don't exist.")
    logger.info("Existing data will NOT be modified.")
    logger.info("=" * 60)

    logger.info("")
    logger.info("Testing database connection...")
    test_connection()

    logger.info("")
    logger.info("Creating tables (if not exist)...")
    create_tables()

    logger.info("")
    logger.info("Setting up permissions...")
    setup_permissions()

    logger.info("")
    logger.info("Current tables in database:")
    tables = list_tables()

    logger.info("")
    logger.info("=" * 60)
    logger.info("MIGRATION COMPLETE")
    logger.info(f"   Tables: {len(tables)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    main()
