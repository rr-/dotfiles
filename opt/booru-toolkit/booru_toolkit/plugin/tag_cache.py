import asyncio
from pathlib import Path
from typing import Any, AsyncIterable, Optional

import sqlalchemy as sa
import sqlalchemy.ext.declarative
import sqlalchemy.ext.mutable
import sqlalchemy.orm
import sqlalchemy.pool

Base: Any = sa.ext.declarative.declarative_base()


class CachedTag(Base):
    __tablename__ = "tag"

    id: int = sa.Column("id", sa.Integer, primary_key=True)
    name: str = sa.Column("name", sa.Text, nullable=False, index=True)
    importance: int = sa.Column("importance", sa.Integer, nullable=False)
    implications: list[str] = sa.Column(
        "implications",
        sa.ext.mutable.MutableList.as_mutable(sa.PickleType),
        nullable=False,
    )


class TagCache:
    def __init__(self, cache_name: str) -> None:
        self._cache: dict[str, CachedTag] = {}
        self._path = Path(
            "~/.cache/tags-{}.sqlite".format(cache_name)
        ).expanduser()

        self._path.parent.mkdir(parents=True, exist_ok=True)
        engine: Any = sa.create_engine(
            "sqlite:///%s" % str(self._path),
            connect_args={"check_same_thread": False},
            poolclass=sa.pool.StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        self._session = sa.orm.scoped_session(
            sa.orm.session.sessionmaker(bind=engine, autoflush=False)
        )

    def exists(self) -> bool:
        return self._session.query(sa.func.count(CachedTag.id)).scalar() > 0

    def add(self, cached_tag: CachedTag) -> None:
        self._session.add(cached_tag)

    def save(self) -> None:
        self._session.commit()

    async def tag_exists(self, tag_name: str) -> bool:
        return (await self._get_tag_by_name(tag_name)) is not None

    async def find_tags(self, query: str) -> list[str]:
        if not query:
            return []
        ret: list[str] = []
        for tag in (
            self._session.query(CachedTag)
            .filter(CachedTag.name.ilike("%{}%".format("%".join(query))))
            .order_by(CachedTag.importance.desc())
            .limit(100)
            .all()
        ):
            self._cache[tag.name] = tag
            ret.append(tag.name)
        return ret

    async def _get_tag_by_name(self, tag_name: str) -> CachedTag:
        if tag_name in self._cache:
            return self._cache[tag_name]

        def work():
            ret = (
                self._session.query(CachedTag)
                .filter(sa.func.lower(CachedTag.name) == tag_name.lower())
                .one_or_none()
            )
            if ret:
                self._session.expunge(ret)
            return ret

        tag = await asyncio.get_event_loop().run_in_executor(None, work)
        self._cache[tag_name] = tag
        return tag

    async def get_tag_real_name(self, tag_name: str) -> Optional[str]:
        tag = await self._get_tag_by_name(tag_name)
        if tag:
            return tag.name
        return None

    async def get_tag_usage_count(self, tag_name: str) -> int:
        tag = await self._get_tag_by_name(tag_name)
        if tag:
            return tag.importance
        return 0

    async def get_tag_implications(self, tag_name: str) -> AsyncIterable[str]:
        to_check = [tag_name]
        visited: set[str] = set([tag_name])
        while to_check:
            tag_name = to_check.pop(0)
            tag = await self._get_tag_by_name(tag_name)
            if tag:
                for implication in tag.implications:
                    if implication not in visited:
                        yield implication
                        visited.add(implication)
                        to_check.append(implication)
