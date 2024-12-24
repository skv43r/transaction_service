"""
Маршруты для работы с транзакциями.
"""
from datetime import datetime, time
from typing import Optional, List
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import schemas
from app.utils import get_current_user, get_db
from common.models.user import User
from common.models.transaction import Transaction

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/transfer", response_model=schemas.TransactionResponse)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> schemas.TransactionResponse:
    """
    Создание новой транзакции между пользователями.

    - Параметры:
        - `transaction`: Объект, содержащий данные о транзакции (ID получателя и сумму).

    - Ответ:
        - Возвращает информацию о созданной транзакции.

    - Ошибки:
        - 400: Если пользователь пытается перевести средства самому себе или недостаточно средств.
        - 404: Если получатель не найден.
    """
    logger.info("Попытка создания транзакции от пользователя %s", current_user.username)

    if current_user.id == transaction.receiver_id:
        logger.warning("Пользователь %s пытается перевести средства самому себе", current_user.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Нельзя перевести средства самому себе")

    receiver = await db.execute(select(User).filter(User.id == transaction.receiver_id))
    receiver = receiver.scalar_one_or_none()
    if not receiver:
        logger.warning("Получатель с ID %d не найден", transaction.receiver_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Получатель не найден")

    if current_user.balance < transaction.amount:
        logger.warning("Недостаточно средств у пользователя %s", current_user.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Недостаточно средств")

    new_transaction = Transaction(
        sender_id=current_user.id,
        receiver_id=transaction.receiver_id,
        amount=transaction.amount,
        status=schemas.TransactionStatus.COMPLETED
    )

    await db.execute(
        select(User).filter(User.id == current_user.id).execution_options(synchronize_session="fetch")
    )
    current_user.balance -= transaction.amount

    await db.execute(
        select(User).filter(User.id == receiver.id).execution_options(synchronize_session="fetch")
    )
    receiver.balance += transaction.amount

    db.add(new_transaction)
    db.add(current_user)
    db.add(receiver)

    await db.commit()
    await db.refresh(new_transaction)

    logger.info("Транзакция успешно создана: %s -> %s, сумма: %.2f", current_user.username, receiver.username, transaction.amount)
    return new_transaction

@router.get("/transactions", response_model=list[schemas.TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
) -> List[schemas.TransactionResponse]:
    """
    Получение списка транзакций с возможностью фильтрации.

    - Параметры:
        - `skip`: Количество пропускаемых транзакций (по умолчанию 0).
        - `limit`: Максимальное количество возвращаемых транзакций (по умолчанию 10).
        - `status`: Фильтр по статусу транзакции (опционально).
        - `start_date`: Начальная дата для фильтрации транзакций (опционально).
        - `end_date`: Конечная дата для фильтрации транзакций (опционально).

    - Ответ:
        - Возвращает список транзакций, соответствующих заданным критериям.

    - Ошибки:
        - 400: Если параметры запроса некорректны.
    """
    logger.info("Получение списка транзакций: skip=%d, limit=%d, status=%s, start_date=%s, end_date=%s",
                skip, limit, status, start_date, end_date)
    query = select(Transaction).offset(skip).limit(limit)

    if status:
        query = query.filter(Transaction.status == status)

    if start_date:
        start_of_day = datetime.combine(start_date, time.min)
        query = query.filter(Transaction.created_at >= start_of_day)

    if end_date:
        end_of_day = datetime.combine(end_date, time.max)
        query = query.filter(Transaction.created_at <= end_of_day)

    result = await db.execute(query)
    transactions = result.scalars().all()

    logger.info("Найдено транзакций: %d", len(transactions))
    return transactions
