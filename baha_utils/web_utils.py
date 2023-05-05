from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import requests
from typing import Union, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
}


class UrlBuilder:
    def __init__(self, url: str) -> None:
        self._url = url
        self._base_url, self._params = self.parse_url()

    # 在原先的url上，再加上任意的parameter
    def __call__(self, **kwargs: dict[str, int]) -> str:
        kwargs_dict = {k: v for k, v in kwargs.items() if v is not None}
        params = {**self._params, **kwargs_dict}
        query_string = urlencode(params)
        if query_string=="":
            return f"{self._base_url}"
        return f"{self._base_url}?{query_string}"

    # 解析url，返回基本路徑以及GET parameter
    def parse_url(self) -> tuple:
        parsed_url = urlparse(self._url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        param_dict = (
            dict([x.split("=") for x in parsed_url.query.split("&")])
            if parsed_url.query != ""
            else {}
        )
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
                    return BeautifulSoup()
                # 設置最大等待時間
                wait = WebDriverWait(driver, 100)
                # 等待網頁全部讀取完畢
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                # 找到所有展開留言按鈕
                elements = driver.find_elements_by_css_selector(
                    "a[id^='showoldCommend_']"
                )

                if len(elements) > 0:
                    # 點選所有按鈕
                    for anchor in elements:
                        anchor.click()
                        time.sleep(0.1)
                    # 檢查使否所有的留言是否都載入完畢
                    while not all(
                        e.get_attribute("style") == "display: none;" for e in elements
                    ):
                        # 等待 1 秒後重新檢查
                        time.sleep(1)
                        # 更新按鈕狀態
                        elements = driver.find_elements_by_css_selector(
                            "a[id^='showoldCommend_']"
                        )

                html = driver.page_source
            soup = BeautifulSoup(html, features="lxml")
            return soup

        if self._page_engine == "requests":
            r = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(r.text, features="lxml")
            return soup
        return BeautifulSoup()
