from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, Sequence

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    """
    Абстрактный класс репозитория, определяющий интерфейс для работы с
    данными.

    Этот класс предоставляет абстрактные методы для добавления,
    поиска и получения данных. Реализации этого интерфейса должны
    предоставлять конкретную логику для взаимодействия с базой данных
    или другим источником данных.
    """

    @abstractmethod
    async def add_one(self, data: Dict[str, Any]) -> Any:
        """Добавляет одну запись в хранилище данных."""
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> Sequence[Any]:
        """Возвращает все записи из хранилища данных."""
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, **filters) -> Optional[Any]:
        """Возвращает одну запись из хранилища данных по заданным фильтрам."""
        raise NotImplementedError


class Repository(AbstractRepository):
    """
    Конкретная реализация репозитория для работы с БД через SQLAlchemy.
    Использует асинхронную сессию для выполнения операций с БД.
    """

    model = None  # Модель данных должна быть указана в подклассе

    def __init__(self, session: AsyncSession):
        """Инициализирует репозиторий с указанием асинхронной сессии для
         работы с БД."""
        self.session = session

    async def add_one(self, data: Dict[str, Any]) -> Any:
        """Добавляет одну запись в базу данных."""
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_all(self) -> Sequence[Any]:
        """Возвращает все записи из базы данных."""
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def get_one(self, **filters) -> Optional[Any]:
        """Возвращает одну запись из базы данных по заданным фильтрам."""
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
