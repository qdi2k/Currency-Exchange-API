from abc import ABC, abstractmethod

from app.db.database import async_session_maker
from app.repositories.user_repository import UserRepository


class IUnitOfWork(ABC):
    """
    Абстрактный базовый класс для Unit of Work (UoW).

    UoW — это паттерн, который управляет транзакциями и обеспечивает
    согласованность данных в приложении. Он объединяет репозитории и
    предоставляет методы для управления транзакциями (commit, rollback).

    Атрибуты:
        user (UserRepository): Репозиторий для работы с пользователями.

    После реализации нового репозитория необходимо его добавить здесь.
    """

    user: UserRepository

    @abstractmethod
    def __init__(self):
        """Инициализация Unit of Work."""
        ...

    @abstractmethod
    async def __aenter__(self):
        """Асинхронный контекстный менеджер для входа в UoW."""
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        """Асинхронный контекстный менеджер для выхода из UoW."""
        ...

    @abstractmethod
    async def commit(self):
        """Фиксация изменений в базе данных."""
        ...

    @abstractmethod
    async def rollback(self):
        """Откат изменений в базе данных."""
        ...


class UnitOfWork(IUnitOfWork):
    """
    Реализация Unit of Work (UoW) для работы с базой данных.

    Этот класс управляет сессией базы данных и предоставляет методы для
    управления транзакциями. Он также инициализирует репозитории для работы
    с данными.

    Атрибуты:
        session_factory: Фабрика для создания асинхронных сессий базы данных.
        session: Текущая сессия базы данных.
        user (UserRepository): Репозиторий для работы с пользователями.
    """
    def __init__(self):
        """Инициализация Unit of Work. Устанавливает фабрику для создания
        асинхронных сессий к БД."""
        self.session_factory = async_session_maker

    async def __aenter__(self):
        """
        Асинхронный вход в контекст UoW. Создает новую сессию базы данных
        и инициализирует репозитории.

        После реализации нового репозитория необходимо его добавить здесь.
        """
        self.session = self.session_factory()

        self.user = UserRepository(self.session)

    async def __aexit__(self, *args):
        """Асинхронный выход из контекста UoW. Выполняет откат изменений и
        закрывает сессию базы данных."""
        await self.rollback()
        await self.session.close()

    async def commit(self):
        """Применяет все изменения, сделанные в рамках текущей транзакции."""
        await self.session.commit()

    async def rollback(self):
        """Отменяет все изменения, сделанные в рамках текущей транзакции."""
        await self.session.rollback()
