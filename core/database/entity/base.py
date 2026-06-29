from typing import Any, TypeVar, Tuple, Dict, List

from sqlalchemy import DateTime
from sqlalchemy import String, Column, CHAR, NCHAR, NVARCHAR, VARCHAR, Text, TEXT
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql.expression import func


@as_declarative()
class IEntity:
    __abstract__ = True
    __tablename__: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def cols(cls,
             to_str: bool = False,
             include_cre: bool = True,
             include_chg: bool = True,
             excludes: List[str] | None = None,
             ) -> List[str] | Dict[str, Any]:

        if not hasattr(cls, '__tablename__'):
            mlist = inspect.getmembers(cls, lambda a: isinstance(a, Column))
            _cols = {t[0]: t[1] for t in mlist}
        else:
            _cols = dict(cls.__table__.columns)

        if excludes is None:
            excludes = []

        if not include_cre:
            excludes += CreEntityBase.cols(to_str=True)
        if not include_chg:
            excludes += ChgEntityBase.cols(to_str=True)

        if len(excludes) > 0:
            for c in excludes:
                _cols.pop(c, None)

        return list(_cols.keys()) if to_str else _cols

    def _props(self):
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    def __repr__(self):
        def column_mapper(col: Column):
            prop = self._props()
            colname = col.key
            quote = "'" if col.type in [String, CHAR, NCHAR, NVARCHAR, VARCHAR, Text, TEXT] else ""
            value = prop.get(colname)
            return f'{colname}={quote}{value}{quote}'

        return f"<{self.__class__.__name__}({','.join(map(column_mapper, self.cols().values()))})>"

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        props = self._props()
        if exclude_none:
            return {k: v for k, v in props.items() if v is not None}
        else:
            return props

    def to_tuple(self, exclude_cols: List[str] = None) -> Tuple:
        attrs = self._props()
        if exclude_cols:
            t = tuple([v for k, v in attrs.items() if k not in exclude_cols])
        else:
            t = tuple(attrs.values())
        return t

    def primary_key(self) -> dict[str, Any]:
        pk = [c for c in self.cols().values() if c.primary_key]
        return {k.name: self.__getattribute__(k.name) for k in pk}


@as_declarative()
class CreEntityBase(IEntity):
    __abstract__ = True

    CRE_USER_ID = Column(String(32), nullable=False, default='SYSTEM')
    CRE_DTTM = Column(DateTime, nullable=False, server_default=func.now())


@as_declarative()
class ChgEntityBase(IEntity):
    __abstract__ = True

    CHG_USER_ID = Column(String(32))
    CHG_DTTM = Column(DateTime)


@as_declarative()
class EntityBase(CreEntityBase, ChgEntityBase):
    __abstract__ = True


TEntity = TypeVar("TEntity", bound=IEntity)

