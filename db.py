from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import config

engine = create_async_engine(config.db.url)
async_session = async_sessionmaker(engine)
