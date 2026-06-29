from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List

import pandas as pd
from rcore.model.base import PageModel

DEFAULT_PAGINATION_PAGE = 0
DEFAULT_PAGINATION_SIZE = 20


class IRepository(ABC):
    def __init__(self, session):
        self.session = session

    @abstractmethod
    async def execute_sql(self, sql: str,
                          param: Dict[str, Any] | None = None,
                          mapper: Callable[[Any], Any] = None,
                          pagination: bool = False,
                          page: int | None = DEFAULT_PAGINATION_PAGE,
                          size: int | None = DEFAULT_PAGINATION_SIZE,
                          log: bool = True,
                          ) -> PageModel[Any] | List[Any]:
        pass

    @abstractmethod
    def execute_sql_to_df(self, sql: str, **kwargs) -> pd.DataFrame:
        pass
