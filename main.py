from typing import Optional
from fastapi import FastAPI
import baha_crawler

app = FastAPI() # 建立一個 Fast API application
crawler = baha_crawler.BahaCrawler()

@app.get("/") # 指定 api 路徑 (get方法)
def read_root():
    return {"Hello": "World"}


@app.get("/baha/get_article_urls_pages")
def get_article_url_list_2(bsn: str, page_start: int, page_end: int):
    return crawler.get_article_urls_pages(bsn, page_start, page_end)

@app.get("/baha/get_article_contents")
def get_article_info(bsn: str, snA:str):
    return crawler.get_article_contents(bsn, snA)



