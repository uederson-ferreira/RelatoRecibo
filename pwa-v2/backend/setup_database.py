"""
Database Setup Script

Executes SQL files to initialize Supabase database.

Usage:
    python setup_database.py

Author: RelatoRecibo Team
Created: 2025-12-09
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")


def get_supabase_client() -> Client:
    """Get Supabase client with service role key."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_role_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")

    return create_client(supabase_url, service_role_key)


def read_sql_file(file_path: str) -> str:
    """Read SQL file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def execute_sql_file(client: Client, file_path: str) -> bool:
    """
    Execute SQL file in Supabase.

    Args:
        client: Supabase client
        file_path: Path to SQL file

    Returns:
        True if successful
    """
    try:
        logger.info(f"Executing {Path(file_path).name}...")

        # Read SQL content
        sql_content = read_sql_file(file_path)

        # Note: Supabase Python client doesn't support raw SQL execution
        # You need to execute these SQL files manually in Supabase SQL Editor
        logger.warning(
            f"⚠️  SQL files must be executed manually in Supabase SQL Editor"
        )
        logger.info(f"   File: {file_path}")

        return False

    except Exception as e:
        logger.error(f"Error executing {file_path}: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("🚀 RelatoRecibo Database Setup")
    logger.info("=" * 60)

    try:
        # Get Supabase client
        logger.info("Connecting to Supabase...")
        client = get_supabase_client()
        logger.success("✓ Connected to Supabase")

        # SQL files directory
        sql_dir = Path(__file__).parent.parent / "sql"

        # SQL files to execute (in order)
        sql_files = [
            "01_schema.sql",
            "02_rls_policies.sql",
            "03_storage_policies.sql",
            "04_functions.sql"
        ]

        logger.info("\n📝 SQL Files to Execute:")
        logger.info("=" * 60)

        for sql_file in sql_files:
            file_path = sql_dir / sql_file

            if not file_path.exists():
                logger.error(f"✗ File not found: {sql_file}")
                continue

            logger.info(f"\n{sql_file}:")
            logger.info(f"  Path: {file_path}")
            logger.info(f"  Size: {file_path.stat().st_size / 1024:.1f} KB")

        # Manual instructions
        logger.info("\n" + "=" * 60)
        logger.info("📋 MANUAL SETUP REQUIRED")
        logger.info("=" * 60)
        logger.info("\nThe Supabase Python client doesn't support raw SQL execution.")
        logger.info("You need to execute these SQL files manually:\n")

        logger.info("1. Go to Supabase Dashboard:")
        logger.info("   https://supabase.com/dashboard/project/euecdkkmnrzqbetzgujw")

        logger.info("\n2. Navigate to: SQL Editor (left sidebar)")

        logger.info("\n3. Execute each SQL file in order:")
        for i, sql_file in enumerate(sql_files, 1):
            file_path = sql_dir / sql_file
            logger.info(f"   {i}. Copy/paste content from: {file_path}")
            logger.info(f"      Click 'Run' to execute")

        logger.info("\n4. Verify tables created:")
        logger.info("   Navigate to: Table Editor")
        logger.info("   Should see: users, reports, receipts tables")

        logger.info("\n5. Verify storage bucket:")
        logger.info("   Navigate to: Storage")
        logger.info("   Should see: 'receipts' bucket")

        logger.info("\n" + "=" * 60)
        logger.success("✓ Setup instructions displayed")
        logger.info("\nAfter executing the SQL files, you can start the backend:")
        logger.info("  cd pwa-v2/backend")
        logger.info("  python -m uvicorn app.main:app --reload")

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
