from urllib.parse import urlencode, urlparse
import requests
from typing import Union, Optional, Type, Any, get_type_hints, get_origin, get_args
import time


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
}


def cast_value_by_key(cls: Type[Any], key: str, value: str):
    hints = get_type_hints(cls)
    try:
        typing_hint_origin = get_origin(hints[key])
        # 若非泛型類
        if typing_hint_origin is None:
            return hints[key](value)
        if typing_hint_origin is Union:
            return get_args(hints[key])[0](value)
        return value
    except:
        return value


def convert_qs_to_dict(cls: Type[Any], query_string: str) -> dict:
    if query_string == "" or query_string == None:
        return {}
    query_params_list = [q.split("=") for q in query_string.split("&")]
    query_params_dict = {k: cast_value_by_key(cls, k, v) for k, v in query_params_list}
    return query_params_dict


class UrlBuilder:
    def __init__(self, cls: Type[Any], url: str) -> None:
        self._url = url
        self._cls = cls
        self._base_url, self._params = self.parse_url()

    # 在原先的url上，再加上任意的parameter
    def __call__(self, **kwargs) -> str:
        kwargs_dict = {k: v for k, v in kwargs.items() if v is not None}
        params = {**self._params, **kwargs_dict}
        query_string = urlencode(params)
        if query_string == "":
            return f"{self._base_url}"
        return f"{self._base_url}?{query_string}"

    # 解析url，返回基本路徑以及GET parameter
    def parse_url(self) -> tuple[str, dict]:
        parsed_url = urlparse(self._url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        param_dict = convert_qs_to_dict(self._cls, parsed_url.query)
        return base_url, param_dict


class WebRequester:
    def __init__(self, page_engine: Optional[str] = "requests") -> None:
        self._page_engine = page_engine

    def __call__(self, url: str) -> BeautifulSoup:
        return self._get_parsed_html(url)

    def _get_parsed_html(self, url: str) -> BeautifulSoup:
        if self._page_engine == "selenium":
            with webdriver.Chrome() as driver:
                try:
                    driver.get(url)
                except WebDriverException:
                    raise RuntimeError("無法載入該網址")
                # 設置最大等待時間
                wait = WebDriverWait(driver, 10)
                # 等待網頁全部讀取完畢
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                # 找到所有展開留言按鈕
                elements = driver.find_elements_by_css_selector(
                    "a[id^='showoldCommend_'][class='more-reply']"
                )

                if len(elements) > 0:
                    # 點選所有按鈕
                    for anchor in elements:
                        anchor.click()
                        time.sleep(0.1)
                    # 檢查使否所有的留言是否都載入完畢
                    while not all(
                        e.get_attribute("style") is not None for e in elements
                    ):
                        # 等待 1 秒後重新檢查
                        time.sleep(1)
                        # 更新按鈕狀態
                        elements = driver.find_elements_by_css_selector(
                            "a[id^='showoldCommend_'][class='more-reply']"
                        )
                html = driver.page_source
            soup = BeautifulSoup(html, features="lxml")
            return soup

        if self._page_engine == "requests":
            r = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(r.text, features="lxml")
            return soup
        raise ValueError("只能選擇requests, selenium作為頁面引擎")
