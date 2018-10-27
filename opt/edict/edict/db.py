import re
import enum
import pathlib
import typing as t
import xdg
import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.ext.declarative
from edict import parser


_Base: t.Any = sa.ext.declarative.declarative_base()
_DB_PATH = pathlib.Path(xdg.XDG_CACHE_HOME) / 'edict2.sqlite'
_session: t.Any = None
_regex_cache: t.Dict[str, t.Pattern] = {}


class SearchSource(enum.Flag):
    KANJI = enum.auto()
    KANA = enum.auto()
    ENGLISH = enum.auto()


class EdictKanji(_Base):
    __tablename__ = 'kanji'

    id: int = sa.Column('id', sa.Integer, primary_key=True)
    entry_id: int = sa.Column(
        'entry_id',
        sa.Integer,
        sa.ForeignKey('entry.id'),
        nullable=False,
        index=True,
    )

    kanji: str = sa.Column('kanji', sa.String, index=True)
    kana: str = sa.Column('kana', sa.String, index=True)
    kanji_tags: t.Sequence[str] = sa.Column('kanji_tags', sa.PickleType)
    kana_tags: t.Sequence[str] = sa.Column('kana_tags', sa.PickleType)


class EdictGlossary(_Base):
    __tablename__ = 'glossary'

    id: int = sa.Column('id', sa.Integer, primary_key=True)
    entry_id: int = sa.Column(
        'entry_id',
        sa.Integer,
        sa.ForeignKey('entry.id'),
        nullable=False,
        index=True,
    )

    english: str = sa.Column('english', sa.String, index=True)
    tags: t.Sequence[str] = sa.Column('tags', sa.PickleType)
    field: t.Optional[str] = sa.Column('field', sa.String)
    related: t.List[str] = sa.Column('related', sa.PickleType)
    common: bool = sa.Column('common', sa.Boolean)


class EdictEntry(_Base):
    __tablename__ = 'entry'

    id: int = sa.Column('id', sa.Integer, primary_key=True)
    glossaries: t.List[EdictGlossary] = sa.orm.relationship(
        EdictGlossary, backref='entry'
    )
    kanji: t.List[EdictKanji] = sa.orm.relationship(
        EdictKanji, backref='entry'
    )
    tags: t.Sequence[str] = sa.Column('tags', sa.PickleType)
    ent_seq: t.Optional[str] = sa.Column('ent_seq', sa.String)


def _re_fn(regex: str, value: str) -> bool:
    if regex not in _regex_cache:
        _regex_cache[regex] = re.compile(regex)
    return _regex_cache[regex].search(value) is not None


@sa.event.listens_for(sa.engine.Engine, 'begin')
def _do_begin(conn):
    conn.connection.create_function('regexp', 2, _re_fn)


def init() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine: t.Any = sa.create_engine('sqlite:///%s' % str(_DB_PATH))

    _Base.metadata.create_all(bind=engine)
    global _session
    _session = sa.orm.scoped_session(
        sa.orm.session.sessionmaker(bind=engine, autoflush=False)
    )


def exists() -> bool:
    if not _DB_PATH.exists():
        return False
    return _session.query(sa.func.count(EdictEntry.id)).scalar() > 0


def put_entry(parsed_entry: parser.EdictEntry) -> None:
    entry = EdictEntry()
    for parsed_glossary in parsed_entry.glossaries:
        glossary = EdictGlossary()
        glossary.english = parsed_glossary.english
        glossary.tags = parsed_glossary.tags
        glossary.field = parsed_glossary.field
        glossary.related = parsed_glossary.related
        entry.glossaries.append(glossary)
    for parsed_japanese in parsed_entry.japanese:
        kanji = EdictKanji()
        kanji.kanji = parsed_japanese.kanji
        kanji.kana = parsed_japanese.kana
        kanji.kanji_tags = parsed_japanese.kanji_tags
        kanji.kana_tags = parsed_japanese.kana_tags
        entry.kanji.append(kanji)
    entry.tags = parsed_entry.tags
    entry.ent_seq = parsed_entry.ent_seq
    _session.add(entry)


def put_entries(parsed_entries: t.Iterable[parser.EdictEntry]) -> None:
    for i, parsed_entry in enumerate(parsed_entries):
        put_entry(parsed_entry)
        if i % 1000 == 0:
            _session.commit()
    _session.commit()


def search_entries_by_regex(
    patterns: t.List[str], sources: enum.Flag
) -> t.List[EdictEntry]:
    entries: t.Dict[int, t.Tuple[int, EdictEntry]] = {}

    if sources & SearchSource.KANJI:
        kanjis = _session.query(EdictKanji).filter(
            sa.and_(
                EdictKanji.kanji.op('regexp')(pattern) for pattern in patterns
            )
        )
        for kanji in kanjis:
            entries[kanji.entry.id] = (len(kanji.kanji), kanji.entry)

    if sources & SearchSource.KANA:
        kanjis = _session.query(EdictKanji).filter(
            sa.and_(
                EdictKanji.kana.op('regexp')(pattern) for pattern in patterns
            )
        )
        for kanji in kanjis:
            entries[kanji.entry.id] = (len(kanji.kana), kanji.entry)

    if sources & SearchSource.ENGLISH:
        glossaries = _session.query(EdictGlossary).filter(
            sa.and_(
                EdictGlossary.english.op('regexp')(pattern)
                for pattern in patterns
            )
        )
        for glossary in glossaries:
            entries[glossary.entry.id] = (
                len(glossary.english),
                glossary.entry,
            )

    return [
        item[1] for item in sorted(entries.values(), key=lambda item: item[0])
    ]
