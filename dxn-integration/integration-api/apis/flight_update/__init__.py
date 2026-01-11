from .api import router
from app.app_factory import create_app

app = create_app(router, "Flight Update Ingestion API")