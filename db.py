from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5432/420cards"
)
async_session = async_sessionmaker(engine)
