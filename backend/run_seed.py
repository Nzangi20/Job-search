import asyncio
from app.seed import seed_defaults

if __name__ == "__main__":
    asyncio.run(seed_defaults())
    print("Database seeding completed successfully.")
