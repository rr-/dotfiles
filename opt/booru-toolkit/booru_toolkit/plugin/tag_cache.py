from pathlib import Path
from typing import Any, Set, List, AsyncIterable
import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import sqlalchemy.ext.mutable


Base: Any = sa.ext.declarative.declarative_base()


class CachedTag(Base):
    __tablename__ = 'tag'

    id: int = sa.Column('id', sa.Integer, primary_key=True)
    name: str = sa.Column('name', sa.Text, nullable=False, index=True)
    importance: int = sa.Column('importance', sa.Integer, nullable=False)
    implications: List[str] = sa.Column(
        'implications', sa.ext.mutable.MutableList.as_mutable(sa.PickleType),
        nullable=False)


class TagCache:
    def __init__(self, cache_name: str) -> None:
        self._path = Path(
            '~/.cache/tags-{}.sqlite'.format(cache_name)).expanduser()

        self._path.parent.mkdir(parents=True, exist_ok=True)
        engine: Any = sa.create_engine('sqlite:///%s' % str(self._path))
        session_maker: Any = (
            sa.orm.session.sessionmaker(bind=engine, autoflush=False))
        Base.metadata.create_all(bind=engine)
        self._session = session_maker()

    def exists(self) -> bool:
        return self._session.query(sa.func.count(CachedTag.id)).scalar() > 0

    def add(self, cached_tag: CachedTag) -> None:
        self._session.add(cached_tag)

    def save(self) -> None:
        self._session.commit()

    async def tag_exists(self, tag_name: str) -> bool:
        return (await self._get_tag_by_name(tag_name)) is not None

    async def find_tags(self, query: str) -> List[str]:
        if not query:
            return []
        return [
            tag.name
            for tag in (
                self._session
                .query(CachedTag)
                .filter(CachedTag.name.ilike('%{}%'.format('%'.join(query))))
                .order_by(CachedTag.importance.desc())
                .limit(250)
                .all())]

    async def _get_tag_by_name(self, tag_name: str) -> CachedTag:
        return (
            self._session
            .query(CachedTag)
            .filter(sa.func.lower(CachedTag.name) == sa.func.lower(tag_name))
            .one_or_none())

    async def get_tag_implications(
            self, tag_name: str) -> AsyncIterable[str]:
        to_check = [tag_name]
        visited: Set[str] = set()
        while bool(to_check):
            text = to_check.pop(0)
            if text in visited:
                continue
            visited.add(text)
            tag = await self._get_tag_by_name(tag_name)
            if tag:
                for implication in tag.implications:
                    yield implication
                    to_check.append(implication)
