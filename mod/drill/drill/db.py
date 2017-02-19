import os
from contextlib import contextmanager
from datetime import datetime
from typing import List, Generator, Any, Optional
from drill import error
import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import sqlalchemy.ext.mutable


def get_db_path() -> str:
    return os.path.expanduser('~/.local/share/drill/decks.sqlite')


engine: Any = sa.create_engine('sqlite:///%s' % os.path.abspath(get_db_path()))
session_maker: Any = sa.orm.session.sessionmaker(bind=engine, autoflush=False)
Base: Any = sa.ext.declarative.declarative_base()


@contextmanager
def session_scope() -> Generator:
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class UserAnswer(Base):
    __tablename__ = 'user_answer'

    id: int = sa.Column('id', sa.Integer, primary_key=True)
    card_id: int = sa.Column(
        'card_id', sa.Integer, sa.ForeignKey('card.id'),
        nullable=False, index=True)
    date: datetime = sa.Column('date', sa.DateTime, nullable=False)
    text: str = sa.Column('text', sa.String, nullable=False)
    is_correct: bool = sa.Column('is_correct', sa.Boolean, nullable=False)


class Card(Base):
    __tablename__ = 'card'

    id: int = sa.Column('id', sa.Integer, primary_key=True)
    deck_id: int = sa.Column(
        'deck_id', sa.Integer, sa.ForeignKey('deck.id'),
        nullable=False, index=True)
    num: int = sa.Column('num', sa.Integer, nullable=False)
    question: str = sa.Column('question', sa.String, nullable=False)
    answers: List[str] = sa.Column(
        'answers', sa.ext.mutable.MutableList.as_mutable(sa.PickleType),
        nullable=False)
    is_active: bool = sa.Column('active', sa.Boolean, nullable=False)
    user_answers = sa.orm.relationship(UserAnswer, cascade='all, delete')
    tags: List[str] = sa.Column(
        'tags', sa.ext.mutable.MutableList.as_mutable(sa.PickleType),
        nullable=False)
    due_date: Optional[datetime] = sa.Column(
        'due_date', sa.DateTime, nullable=True)

    first_answer_date = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.min(UserAnswer.date)])
        .where(UserAnswer.card_id == id)
        .correlate_except(UserAnswer))

    total_answer_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(UserAnswer.id)])
        .where(UserAnswer.card_id == id)
        .correlate_except(UserAnswer))

    correct_answer_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(UserAnswer.id)])
        .where(UserAnswer.card_id == id)
        .where(UserAnswer.is_correct == 1)
        .correlate_except(UserAnswer))

    incorrect_answer_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(UserAnswer.id)])
        .where(UserAnswer.card_id == id)
        .where(UserAnswer.is_correct == 0)
        .correlate_except(UserAnswer))


class Deck(Base):
    __tablename__ = 'deck'

    id: int = sa.Column('id', sa.Integer, primary_key=True)
    cards: List[Card] = sa.orm.relationship(Card, cascade='all, delete')
    name: str = sa.Column('name', sa.String, nullable=False)
    description: Optional[str] = sa.Column(
        'description', sa.String, nullable=True)


def init() -> None:
    os.makedirs(os.path.dirname(get_db_path()), exist_ok=True)
    Base.metadata.create_all(bind=engine)


def try_get_deck_by_name(session: Any, name: str) -> Optional[Deck]:
    deck_count = session.query(sa.func.count(Deck.id)).scalar()
    if not name:
        if deck_count < 1:
            raise error.DeckNotFoundError(
                'No deck available. Create one first.')
        if deck_count > 1:
            raise error.AmbiguousDeckError(
                'Need to specify which deck to use.')
        return session.query(Deck).one()
    return session.query(Deck).filter(Deck.name == name).one_or_none()


def get_deck_by_name(session: Any, name: str) -> Deck:
    deck = try_get_deck_by_name(session, name)
    if deck:
        return deck
    raise error.DeckNotFoundError('A deck with name %r doesn\'t exist' % name)


def try_get_card_by_num(session: Any, deck: Deck, num: int) -> Optional[Card]:
    return session.query(Card) \
        .filter(Card.deck_id == deck.id) \
        .filter(Card.num == num) \
        .one_or_none()


def get_card_by_num(session: Any, deck: Deck, num: int) -> Card:
    card = try_get_card_by_num(session, deck, num)
    if card:
        return card
    raise error.CardNotFoundError('A card with ID %r doesn\'t exist' % num)


def get_max_card_num(session: Any, deck: Deck) -> int:
    return session \
        .query(sa.func.max(Card.num)) \
        .filter(Card.deck_id == deck.id) \
        .scalar()
