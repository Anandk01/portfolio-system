from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from core.config import settings

client: AsyncIOMotorClient | None = None
engine: AIOEngine | None = None

async def init_db():
    global client, engine
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    engine = AIOEngine(client=client, database=settings.MONGODB_DB_NAME)
    
def get_engine() -> AIOEngine:
    if engine is None:
        raise RuntimeError("Database not initialized")
    return engine
