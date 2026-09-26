import ssl
from collections.abc import AsyncGenerator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

db_url = settings.database_url
connect_args: dict = {}

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+aiomysql://", 1)
elif db_url.startswith("mysql+pymysql://"):
    db_url = db_url.replace("mysql+pymysql://", "mysql+aiomysql://", 1)

if "mysql+aiomysql" in db_url:
    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query)

    has_ssl = False
    for ssl_key in ["ssl-mode", "sslmode", "ssl_mode", "ssl"]:
        if ssl_key in query_params:
            val = query_params.pop(ssl_key)[0].lower()
            if val not in ["disabled", "false", "0", "off", "none"]:
                has_ssl = True

    if has_ssl:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx

    new_query = urlencode(query_params, doseq=True)
    db_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))

engine = create_async_engine(
    db_url,
    echo=settings.debug,
    future=True,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    from app import models  # noqa: F401
    from sqlalchemy import inspect, text

    def sync_tables(sync_conn):
        # 1. Create missing tables
        Base.metadata.create_all(sync_conn)

        # 2. Add missing columns and relax legacy NOT NULL columns on existing tables
        inspector = inspect(sync_conn)
        existing_tables = set(inspector.get_table_names())

        for table_name, table in Base.metadata.tables.items():
            if table_name in existing_tables:
                db_cols_info = inspector.get_columns(table_name)
                existing_cols = {c["name"]: c for c in db_cols_info}
                model_col_names = {col.name for col in table.columns}

                # Add missing columns defined on the model
                for col in table.columns:
                    if col.name not in existing_cols:
                        try:
                            col_type = col.type.compile(sync_conn.dialect)
                        except Exception:
                            col_type = "VARCHAR(255)"

                        col_type_str = str(col_type)

                        if "postgresql" in sync_conn.dialect.name:
                            alter_sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col.name}" {col_type_str}'
                        elif "sqlite" in sync_conn.dialect.name:
                            alter_sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col.name}" {col_type_str}'
                        else:
                            alter_sql = f'ALTER TABLE `{table_name}` ADD COLUMN `{col.name}` {col_type_str}'

                        try:
                            sync_conn.execute(text(alter_sql))
                            print(f"Added missing column '{col.name}' to table '{table_name}'")
                        except Exception as e:
                            print(f"Notice: could not add missing column {table_name}.{col.name}: {e}")

                # Relax NOT NULL on legacy columns not present in the current model
                for col_name, col_info in existing_cols.items():
                    if col_name not in model_col_names:
                        if not col_info.get("nullable", True) and col_info.get("default") is None:
                            col_type_str = str(col_info.get("type", "VARCHAR(255)"))
                            if "postgresql" in sync_conn.dialect.name:
                                alter_sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{col_name}" DROP NOT NULL'
                            elif "sqlite" not in sync_conn.dialect.name:
                                alter_sql = f'ALTER TABLE `{table_name}` MODIFY COLUMN `{col_name}` {col_type_str} NULL'
                            else:
                                alter_sql = None

                            if alter_sql:
                                try:
                                    sync_conn.execute(text(alter_sql))
                                    print(f"Relaxed NOT NULL constraint on legacy column '{table_name}.{col_name}'")
                                except Exception as e:
                                    print(f"Notice: could not alter legacy column {table_name}.{col_name}: {e}")

    async with engine.begin() as conn:
        await conn.run_sync(sync_tables)

