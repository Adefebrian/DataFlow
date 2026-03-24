import sys

sys.path.insert(0, "/Users/brianeedsleep/Documents/Vibecode")

import asyncio
from src.db.database import db, create_tables


async def main():
    print("Creating database tables...")
    await db.connect()

    if db.pool:
        await create_tables(db)
        print("Tables created successfully!")

        result = await db.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print(f"\nTables in database:")
        for row in result:
            print(f"  - {row['table_name']}")
    else:
        print("No database connection - skipping table creation")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
