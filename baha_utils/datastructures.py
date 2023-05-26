from typing import Union, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Comment:
    comment_id: str
    user_id: str
    user_name: str
    content: str
    floor: int
    publish_time: datetime
    gp_count: int
    bp_count: int


@dataclass(frozen=True)
class Reply:
    reply_id: str
    user_id: str
    user_name: str
    content: str
    floor: int
    publish_time: datetime
    gp_count: int
    bp_count: int
    comments: list[Comment]


@dataclass(frozen=True)
class Ariticle:
    title: str
    url: str
    replys: list[Reply]


class QueryParams:
    @dataclass
    class CPage:
        bsn: int
        snA: int
        page: Optional[int] = None
        tnum: Optional[int] = None
        to: Optional[int] = None

        @classmethod
        def attributes(cls) -> list:
            return list(vars(cls(bsn=0, snA=0)))

    @dataclass
    class BPage:
        bsn: int
        subbsn: Optional[int] = None
        page: Optional[int] = None
        qt: Optional[int] = None
        q: Optional[int] = None

        @classmethod
        def attributes(cls) -> list:
            return list(vars(cls(bsn=0)))

    @dataclass
    class SearchPage:
        bsn: int
        q: str
        page: Optional[int] = None
        type: Optional[str] = None
        field: Optional[str] = None
        author: Optional[str] = None
        sortType: Optional[str] = None
        advancedSearch: Optional[int] = None
        subbsn: Optional[int] = None
        dateType: Optional[str] = None
        startDate: Optional[str] = None
        endDate: Optional[str] = None
        gp: Optional[int] = None
        
        @classmethod
        def attributes(cls) -> list:
            return list(vars(cls(bsn=0, q='0')))


@dataclass
class WebArguments:
    soup: Optional[BeautifulSoup] = None
    url: Optional[str] = None
    query_params: Optional[Union[QueryParams.BPage, QueryParams.CPage, QueryParams.SearchPage]] = None
    page_engine: Optional[str] = "requests"

    def __post_init__(self):
        args = vars(self)
        args_is_not_none = [
            1 if v is not None else 0 for k, v in args.items() if k != "page_engine"
        ]
        if sum(args_is_not_none) != 1:
            raise ValueError("只能給定soup, url, query_params三種引數其中之一")
