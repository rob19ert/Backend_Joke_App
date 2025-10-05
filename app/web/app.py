from aiohttp.web import Application as AiohttpApplication, View as AiohttpView, Request as AiohttpRequest, run_app as aiohttp_run_app

from app.store import setup_store
from app.store.crm.accessor import CrmAccessor
from app.store.database.database import Database
from app.web.middlewares import setup_middleware
from app.web.routes import setup_routes
from aiohttp_apispec import setup_aiohttp_apispec

class Application(AiohttpApplication):
    database: Database | None = None
    crm_accessor: CrmAccessor | None = None

class Request(AiohttpRequest):
    @property
    def app(self) -> Application:
        return super().app

class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request


app = Application()

def run_app():
    setup_routes(app)
    setup_aiohttp_apispec(
        app,
        title="Joke App",
        url='/docs/json',
        swagger_path='/docs',
        securityDefinitions={
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Bearer token"
            }
        },
    )
    setup_middleware(app)
    setup_store(app)
    aiohttp_run_app(app, host = "127.0.0.1", port=8000)

