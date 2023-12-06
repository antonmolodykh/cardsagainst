from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://postgres:huivoinekartymne@185.76.14.208:5432/420cards"
)
async_session = async_sessionmaker(engine)
