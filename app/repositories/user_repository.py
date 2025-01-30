from typing import Dict, Any

from sqlalchemy import update

from app.db.models import User
from app.repositories.base_repository import Repository


class UserRepository(Repository):
    model = User

    async def update_one(self, user_id: int, data: Dict[str, Any]) -> None:
        """Обновляет одну запись в базе данных по user_id."""
        stmt = update(self.model).where(
            self.model.id == user_id
        ).values(**data)
        await self.session.execute(stmt)
