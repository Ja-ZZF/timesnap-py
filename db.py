from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

DB_USER = 'harmonyUser'
DB_PASS = 'abc123456'
DB_HOST = '47.117.0.254'
DB_PORT = 3306
DB_NAME = 'timesnap'

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine: Engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
