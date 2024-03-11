from fastapi import FastAPI, __version__
from loguru import logger
from uvicorn import Config, Server

from app.core.example.api import example_router
from app.core.system.api import system_router
from app.database import Database
from app.utils.log_handler import init_logging
from settings.config import Settings, dump_config, get_settings

config: Settings = get_settings()


class Application:
    def __init__(self, app_config: Settings):
        self.config = app_config
        self.app: FastAPI

    def setup(self) -> FastAPI:
        self.app: FastAPI = FastAPI(
            version=__version__,
            title="Backend template",
            description="Template service",
            debug=config.DEBUG,
        )

        self.add_middlewares(config)
        self.register_urls()
        self.configure_hooks()

        return self.app

    def configure_hooks(self) -> None:
        self.app.add_event_handler("startup", self.create_database_pool)
        self.app.add_event_handler("shutdown", self.close_database_pool)

    def register_urls(self) -> None:
        self.app.include_router(system_router, prefix="/api/v1")
        self.app.include_router(example_router, prefix="/api/v1/examples")

    def add_middlewares(self, settings: Settings) -> None:
        """Add your middlewares here."""

    def create_database_pool(self) -> None:
        databases: dict = {}
        settings = self.config
        for db_alias in settings.DB_READABLE_NAMES:
            uri = getattr(settings, f"{db_alias}_SQLALCHEMY_DATABASE_URI")
            pool_size = getattr(settings, f"{db_alias}_POOL_SIZE")
            db = Database(
                db_connect_url=uri,
                db_alias=db_alias,
                connect_kwargs=dict(**Database.CONNECT_KWARGS, pool_size=pool_size),
                debug=settings.DEBUG,
            )
            logger.info("creating database connection for {}", db_alias)
            setattr(self.app, db_alias, db)
            databases[db_alias] = db
        self.app.state.databases = databases

    async def close_database_pool(self) -> None:
        for db_alias, db in self.app.state.databases.items():
            logger.info("closing database pool for db {}", db_alias)
            try:
                await db.disconnect()
            except Exception as exc:
                logger.warning(
                    "failed to close database pool {} due to {}",
                    db_alias,
                    exc,
                )
                continue


def get_app(app_configuration: Settings = config) -> FastAPI:
    application = Application(app_configuration).setup()
    logger.debug("Loaded configuration\n %s" % dump_config(app_configuration))  # noqa
    init_logging(app_configuration)

    return application


if __name__ == "__main__":
    app = get_app()
    server = Server(
        Config(
            app=app,
            host=config.APP_HOST,
            port=config.APP_PORT,
            log_level=config.LOG_LEVEL,
        )
    )
    server.run()
