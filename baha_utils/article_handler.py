import time
import random as rd
from typing import Union, Optional, Callable
import json
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag
import abc
from dataclasses import dataclass, field, asdict

from .web_utils import WebRequester, UrlBuilder
from .datastructures import WebArguments, QueryParams, Ariticle, Reply, Comment


BAHA_URL = "https://forum.gamer.com.tw"
B_PAGE = "B.php"
C_PAGE = "C.php"

WAIT_TIME_FN = lambda: (rd.random() * 4) + 1
INF = 999999


class BasicHandler(abc.ABC):
    def __init__(self, web_args: WebArguments) -> None:
        self._page_engine = web_args.page_engine
        self._web_requester = WebRequester(self._page_engine)
        self._url_builder: UrlBuilder
        self._soup: BeautifulSoup
        self.url: str
        self._query_params_c: QueryParams.CPage
        if web_args.soup is not None:
            self._soup = web_args.soup
            self.url = self._soup.select_one(
                "head>link[rel='canonical'][href^='https://forum.gamer.com.tw/C.php']"
            ).get("href")
            print(self.url)
            self._url_builder = UrlBuilder(self.url)
            _, params_dict = self._url_builder.parse_url()
            self._query_params_c = QueryParams.CPage(**params_dict)
        if web_args.url is not None:
            self.url = web_args.url
            self._url_builder = UrlBuilder(self.url)
            _, params_dict = self._url_builder.parse_url()
            self._query_params_c = QueryParams.CPage(**params_dict)
            self._soup = self._web_requester(self.url)
        if web_args.query_params is not None:
            self._query_params_c = web_args.query_params
            self._url_builder = UrlBuilder(f"{BAHA_URL}/{C_PAGE}")
            self.url = self._url_builder(**asdict(self._query_params_c))
            self._soup = self._web_requester(self.url)


class TextHandler(BasicHandler):
    def __init__(self, web_args: WebArguments) -> None:
        super().__init__(web_args)

    def get_text(
        self,
        reply_id: Optional[str] = None,
        comment_id: Optional[str] = None,
        text_only: Optional[int] = 1,
    ) -> str:
        if all([reply_id is not None, comment_id is not None]):
            raise ValueError("只能給定reply_id, comment_id兩種引數其中之一")

        if reply_id is not None:
            elements = self._soup.select_one(
                f"""section[id="{reply_id}"] div[class="c-article__content"]"""
            )
        elif comment_id is not None:
            elements = self._soup.select_one(
                f"""div[id="{comment_id}"] span[class^="comment_content"]"""
            )
        else:
            raise ValueError("沒有給予reply_id或comment_id")

        if text_only:
            return elements.text

        return TextHandler._extract_text(elements)

    @staticmethod
    def _extract_text(tag: Tag) -> str:
        def extract_text_dfs(elements: Union[Tag, NavigableString], result_text: list):
            # 如果是NavigableString
            if not isinstance(elements, Tag):
                result_text += [elements]
                return

            # 如果是youtube撥放器
            if (
                elements.name == "div"
                and elements.has_attr("class")
                and "videoWrapper" in elements["class"]
                and "video-youtube" in elements["class"]
            ):
                ytb_url = elements.select_one("iframe[data-src]").get("data-src")
                ytb_url_data = {"ytb_url": ytb_url}
                result_text += [json.dumps(ytb_url_data, ensure_ascii=False)]

            # 如果是anchor元素
            if elements.name == "a" and elements.has_attr("href"):
                hyperlink_data = {
                    "hyperlink": elements.get("href"),
                    "text": elements.text,
                }
                result_text += [json.dumps(hyperlink_data, ensure_ascii=False)]

            # leaf element 如果沒有存在子元素
            if not elements.find_all(recursive=False):
                # image
                if elements.name == "img" and elements.has_attr("data-src"):
                    img_data = {"image": elements.get("data-src")}
                    result_text += [json.dumps(img_data, ensure_ascii=False)]
                # emotion
                if (
                    elements.name == "img"
                    and elements.has_attr("src")
                    and elements.has_attr("border")
                ):
                    img_data = {"emotion": elements.get("src")}
                    result_text += [json.dumps(img_data, ensure_ascii=False)]

                # 取得文字
                result_text += [elements.text]
                return

            for element in elements.contents:
                extract_text_dfs(element, result_text)

        text = []
        extract_text_dfs(tag, text)
        # 過濾掉可能存在於list的None物件
        text_filtered = list(filter(None, text))
        return " ".join(text_filtered)


class CommentHandler(TextHandler):
    def __init__(self, web_args: WebArguments) -> None:
        super().__init__(web_args)

    def _get_comment_contents(
        self, reply_id: str, text_only: Optional[int] = 1
    ) -> list:
        comments = self._soup.select(
            f"section[id='{reply_id}'] div[id^='Commendcontent_']"
        )
        comment_contents = []
        for comment in comments:
            comment_id = comment.get("id")
            comment_content = Comment(
                comment_id=comment_id,
                user_id=comment.select_one("img[data-gamercard-userid]").get(
                    "data-gamercard-userid"
                ),
                user_name=comment.select_one(
                    "a[class='reply-content__user']"
                ).text,
                content=self.text(comment_id=comment_id, text_only=text_only),
                floor=int(
                    comment.select_one("div[name='comment_floor']")
                    .text
                    .replace("B", "")
                ),
                publish_time=datetime.strptime(
                    comment.select_one("div[data-tippy-content]")
                    .get("data-tippy-content")
                    .replace("留言時間", ""),
                    " %Y-%m-%d %H:%M:%S",
                ),
                gp_count=int(comment.select_one("a[data-gp]").get("data-gp")),
                bp_count=int(comment.select_one("a[data-bp]").get("data-bp")),
            )
            comment_contents += [comment_content]
        return comment_contents


class ReplyHandler(CommentHandler):
    def __init__(self, web_args: WebArguments) -> None:
        super().__init__(web_args)

    def _get_reply_contents(self, text_only: Optional[int] = 1) -> list:
        replys = self._soup.select("section[id^='post_']")
        reply_contents = []
        for reply in replys:
            reply_id = reply.get("id")
            reply_content = Reply(
                reply_id=reply_id,
                user_id=reply.select_one(".userid").text,
                user_name=reply.select_one(".username").text,
                content=self.text(reply_id=reply_id, text_only=text_only),
                floor=int(reply.select_one(".floor").get("data-floor")),
                publish_time=datetime.strptime(
                    reply.select_one(".edittime").get("data-mtime"), "%Y-%m-%d %H:%M:%S"
                ),
                gp_count=1000
                if reply.select_one(".postgp span").text == "爆"
                else int(reply.select_one(".postgp span").text)
                if reply.select_one(".postgp span").text != "-"
                else 0,
                bp_count=500
                if reply.select_one(".postbp span").text == "X"
                else int(reply.select_one(".postbp span").text)
                if reply.select_one(".postbp span").text != "-"
                else 0,
                comments=self._get_comment_contents(reply_id, text_only=text_only),
            )
            reply_contents += [reply_content]
        return reply_contents


class ArticleHandler(ReplyHandler):
    def __init__(self, web_args: WebArguments) -> None:
        super().__init__(web_args)

    def get_article_content(
        self,
        text_only: Optional[int] = 1,
        sub_page_limit_num: Optional[int] = INF,
        sub_page_wait_time_fn: Optional[Callable] = WAIT_TIME_FN,
    ) -> dict:
        article_title = self._soup.select_one("h1[class^='c-post__header__title']")
        article_title = article_title.text

        sub_pages_num = self._get_sub_pages_num()
        limited_sub_pages_num = min(sub_page_limit_num, sub_pages_num)

        reply_contents = []
        for sub_page in range(limited_sub_pages_num):
            sub_page = sub_page + 1
            if sub_page == 1:
                reply_content = self._get_reply_contents(text_only=text_only)
                reply_contents += reply_content
            else:
                query_params_c = self._query_params_c
                query_params_c.page = sub_page
                reply_content = ReplyHandler(
                    WebArguments(query_params=query_params_c)
                )._get_reply_contents(text_only=text_only)
                reply_contents += reply_content
            time.sleep(sub_page_wait_time_fn())

        article_content = Ariticle(
            title=article_title,
            url=self.url,
            replys=reply_contents,
        )
        return article_content

    def _get_sub_pages_num(self) -> int:
        last_page_btn = self._soup.select_one(".BH-pagebtnA > a:last-of-type")
        article_total_page = int(last_page_btn.text)
        return article_total_page
