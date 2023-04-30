from typing import Optional, Union
from fastapi import FastAPI
import baha_crawler
import random as rd

app = FastAPI()  # 建立一個 Fast API application
crawler = baha_crawler.BahaCrawler()


@app.get("/")  # 指定 api 路徑 (get方法)
def read_root():
    return {"Hello": "World"}


@app.get("/baha/get_article_urls_pages")
def get_article_urls_pages(
    bsn: Union[int, str],
    start_page: Union[int, str],
    end_page: Optional[Union[int, str]],
) -> list:
    return crawler.get_article_urls_pages(bsn, start_page, end_page)


@app.get("/baha/get_article_contents")
def get_article_contents(
    bsn: Union[int, str], snA: Union[int, str], wait_time: Optional[Union[int, float]]
) -> dict:
    return crawler.get_article_contents(bsn, snA, wait_time)
