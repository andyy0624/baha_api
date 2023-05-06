from typing import Union, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from bs4 import BeautifulSoup

@dataclass(frozen=True)
class Comment:
    __slots__ = [
        "comment_id",
        "user_id",
        "user_name",
        "content",
        "floor",
        "publish_time",
        "gp_count",
        "bp_count",
    ]
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
    __slots__ = [
        "reply_id",
        "user_id",
        "user_name",
        "content",
        "floor",
        "publish_time",
        "gp_count",
        "bp_count",
        "comments",
    ]
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
    __slots__ = ["title", "url", "replys"]
    title: str
    url: str
    replys: list[Reply]


@dataclass
class QuerryParams:
    bsn: int
    snA: int
    page: Optional[int] = None
    tnum: Optional[int] = None


@dataclass
class WebArguments:
    soup: Optional[BeautifulSoup] = None
    url: Optional[str] = None
    querry_params: Optional[QuerryParams] = None
    page_engine: Optional[str] = "requests"

    def __post_init__(self):
        args = vars(self)
        del args["page_engine"]
        args_is_not_none = [1 if x is not None else 0 for x in args.values()]
        if sum(args_is_not_none) != 1:
            raise ValueError("只能給定soup, url, querry_params三種引數其中之一")