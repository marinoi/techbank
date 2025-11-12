import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .utils import card_exists_or_404, transaction_exists_or_404, transaction_ownership_or_404
from ..common.db.orm import get_async_session
from ..common.security.router import RuledAPIRouter
from ..common.security.roles import Role

from .routes import AdminRoutes, ADMIN_ROUTER_PREFIX
from ..models.models import Card, CardTransaction
from ..schemas.schemas import CardOut, CardDetailsOut, TransactionOut, TransactionDetailsOut


administration_api = RuledAPIRouter(prefix=ADMIN_ROUTER_PREFIX,
                                    tags=["administration"],
                                    allowed_roles=[Role.ADMIN])


@administration_api.get(AdminRoutes.CARDS.value, response_model=list[CardOut], status_code=status.HTTP_200_OK)
async def get_cards(session: AsyncSession = Depends(get_async_session)):
    cards = await Card.get_all(session)
    return cards

@administration_api.get(AdminRoutes.CARD.value, response_model=list[CardOut], status_code=status.HTTP_200_OK)
async def get_card(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    user_cards = await Card.get_by_user_id(session, user_id)
    return user_cards


@administration_api.get(AdminRoutes.CARD_DETAILS.value, response_model=CardDetailsOut, status_code=status.HTTP_200_OK)
async def get_card_details(card_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    card = await Card.get_by_id(session, card_id)
    card_exists_or_404(card)
    return card


@administration_api.get(AdminRoutes.CARD_TRANSACTIONS.value, response_model=list[TransactionOut], status_code=status.HTTP_200_OK)
async def get_card_transactions(card_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    card = await Card.get_by_id(session, card_id, load_transactions=True)
    card_exists_or_404(card)
    return card.transactions


@administration_api.get(AdminRoutes.TRANSACTION_DETAILS.value, response_model=TransactionDetailsOut, status_code=status.HTTP_200_OK)
async def get_transaction_details(card_id: uuid.UUID, transaction_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    card = await Card.get_by_id(session, card_id)
    card_exists_or_404(card)

    transaction = await CardTransaction.get_by_id(session, transaction_id)
    transaction_exists_or_404(transaction)
    transaction_ownership_or_404(transaction, card)

    return transaction


@administration_api.patch(AdminRoutes.BLOCK_CARD.value, status_code=status.HTTP_200_OK)
async def patch_block_card(card_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    async with session.begin():
        card = await Card.get_by_id(session, card_id, for_update=True)
        card_exists_or_404(card)
        card.is_active = False

    return {"detail": "card-blocked-successfully"}


@administration_api.patch(AdminRoutes.UNBLOCK_CARD.value, status_code=status.HTTP_200_OK)
async def patch_unblock_card(card_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    async with session.begin():
        card = await Card.get_by_id(session, card_id, for_update=True)
        card_exists_or_404(card)
        card.is_active = True

    return {"detail": "card-unblocked-successfully"}
