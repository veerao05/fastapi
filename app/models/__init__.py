# Import all models here so SQLAlchemy registers them with Base.metadata
# before create_all() is called at startup.
from app.models.order import Order  # noqa: F401
from app.models.user import User  # noqa: F401
