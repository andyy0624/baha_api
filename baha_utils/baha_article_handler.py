import time
import random as rd
from typing import Union, Optional
import json
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag
import abc

from .web_utils import WebRequester, UrlBuilder


BAHA_URL = "https://forum.gamer.com.tw"
B_PAGE = "B.php"
C_PAGE = "C.php"


class TextHandler(abc.ABC):
    def __init__(self, soup: Optional[BeautifulSoup] = None) -> None:
        self._soup = soup

    def _get_text(self, **kwargs) -> str:
        if "reply_id" in kwargs:
            elements = self._soup.select_one(
                f"""section[id="{kwargs['reply_id']}"] div[class="c-article__content"]"""
            )
        elif "comment_id" in kwargs:
            elements = self._soup.select_one(
                f"""div[id="{kwargs['comment_id']}"] span[class="comment_content"]"""
            )
        else:
            return "Error"
        return TextHandler._extract_text(elements)

    @staticmethod
    def _extract_text(tag: Tag) -> str:
        def extract_text_dfs(elements, result_text: list):
            # 如果是NavigableString
            if not isinstance(elements, Tag):
                result_text += [elements]
                return

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
                # hyperlink
                if (
                    elements.name == "a"
                    and elements.has_attr("href")
                    and elements.has_attr("target")
                    and elements["target"] == "_blank"
                ):
                    hyperlink_data = {
                        "hyperlink": elements.get("href"),
                        "text": elements.get_text(),
                    }
                    result_text += [json.dumps(hyperlink_data, ensure_ascii=False)]
                result_text += [elements.get_text()]
                return

            for element in elements.contents:
                extract_text_dfs(element, result_text)

        text = []
        extract_text_dfs(tag, text)
        text_filtered = list(filter(None, text))
        return " ".join(text_filtered)


class CommentHandler(TextHandler):
    def __init__(self, soup: Optional[BeautifulSoup] = None) -> None:
        super().__init__(soup)

    def _get_comment_contents(self, reply_id: str) -> list:
        comments = self._soup.select(
            f"section[id='{reply_id}'] div[id^='Commendcontent_']"
        )
        comment_contents = []
        for comment in comments:
            comment_id = comment.get("id")
            comment_content = {
                "comment_id": comment_id,
                "user_id": comment.select_one("img[data-gamercard-userid]").get(
                    "data-gamercard-userid"
                ),
                "user_name": comment.select_one("a[class='reply-content__user']").text,
                "content": self._get_text(comment_id=comment_id),
                "floor": comment.select_one("div[name='comment_floor']").text,
                "publish_time": datetime.strptime(
                    comment.select_one("div[data-tippy-content]")
                    .get("data-tippy-content")
                    .replace("留言時間", ""),
                    " %Y-%m-%d %H:%M:%S",
                ),
                # "edit_time": datetime.strptime(
                #     comment.select_one("div[data-tippy-content]")
                #     .getText()
                #     .replace(" 編輯", ""),
                #     " %Y-%m-%d %H:%M:%S",
                # ),
                "gp_count": int(comment.select_one("a[data-gp]").get("data-gp")),
                "bp_count": int(comment.select_one("a[data-bp]").get("data-bp")),
            }
            comment_contents += [comment_content]
        return comment_contents


class ReplyHandler(CommentHandler):
    def __init__(self, soup: Optional[BeautifulSoup] = None) -> None:
        super().__init__(soup)

    def _get_reply_contents(self) -> list:
        replys = self._soup.select("section[id^='post_']")
        reply_contents = []
        for reply in replys:
            reply_id = reply.get("id")
            reply_content = {
                "reply_id": reply_id,
                "user_id": reply.select_one(".userid").text,
                "user_name": reply.select_one(".username").text,
                "content": self._get_text(reply_id=reply_id),
                "floor": int(reply.select_one(".floor").get("data-floor")),
                "publish_time": datetime.strptime(
                    reply.select_one(".edittime").get("data-mtime"), "%Y-%m-%d %H:%M:%S"
                ),
                # "edit_time": datetime.strptime(
                #     reply.select_one(".edittime").text.replace(" 編輯", ""),
                #     "%Y-%m-%d %H:%M:%S",
                # ),
                "gp_count": 1000
                if reply.select_one(".postgp span").text == "爆"
                else int(reply.select_one(".postgp span").text)
                if reply.select_one(".postgp span").text != "-"
                else 0,
                "bp_count": 500
                if reply.select_one(".postbp span").text == "X"
                else int(reply.select_one(".postbp span").text)
                if reply.select_one(".postbp span").text != "-"
                else 0,
                "comments": self._get_comment_contents(reply_id),
            }
            reply_contents += [reply_content]
        return reply_contents


class ArticleHandler(ReplyHandler):
    def __init__(
        self,
        bsn: Union[int, str],
        snA: Union[int, str],
        page_engine: Optional[str] = "requests",
    ) -> None:
        super().__init__()
        self._web_requester = WebRequester(page_engine)
        self._url_builder = UrlBuilder(f"{BAHA_URL}/{C_PAGE}")
        self.bsn = bsn
        self.snA = snA
        self.url = self._url_builder(bsn=self.bsn, snA=self.snA)
        # 初始化時設定soup (解析後的html)
        # self._soup = self._web_requester(self.url)
        super().__init__(self._web_requester(self.url))

    def get_article_contents(
        self,
        limit_page: Optional[int] = float("inf"),
        wait_time: Optional[Union[int, float]] = (rd.random() * 4) + 1,
    ) -> dict:
        article_title = self._soup.select_one("h1[class^='c-post__header__title']")
        if article_title is None:
            return {"Error": "抓不到該文章標題", "URL": url}
        article_title = article_title.text

        article_total_page = self._get_article_pages_num()
        article_total_page = min(limit_page, article_total_page)

        reply_contents = []
        for page in range(article_total_page):
            if page == 0:
                reply_content = self._get_reply_contents()
                reply_contents += reply_content
            else:
                url = self._url_builder(bsn=self.bsn, snA=self.snA, page=page + 1)
                soup = self._web_requester(url)
                reply_content = ReplyHandler(soup)._get_reply_contents()
                reply_contents += reply_content
            time.sleep(wait_time)

        article_content = {
            "title": article_title,
            "url": self.url,
            "reply": reply_contents,
        }
        return article_content

    def _get_article_pages_num(self) -> int:
        last_page_btn = self._soup.select_one(".BH-pagebtnA > a:last-of-type")
        article_total_page = int(last_page_btn.text)
        return article_total_page
