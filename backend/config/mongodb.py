import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    mongodb_uri = os.getenv("MONGODB_URI")
    # Use certifi's CA bundle to fix SSL cert verification on macOS
    client = AsyncIOMotorClient(
        f"{mongodb_uri}/prescripto",
        tlsCAFile=certifi.where()
    )
    db = client.prescripto
    # Ping to verify connection
    await client.admin.command("ping")
    print("Database Connected")


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
