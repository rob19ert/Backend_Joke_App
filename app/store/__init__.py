import typing

from app.store.crm.accessor import CrmAccessor
from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application

class Store:
    pass


def setup_store(app: "Application"):
    app.database = Database(app)
    app.crm_accessor = CrmAccessor(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)