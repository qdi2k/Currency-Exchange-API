from app.db.models import User
from app.repositories.base_repository import Repository


class UserRepository(Repository):
    model = User
