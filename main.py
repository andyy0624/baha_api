from typing import Optional, Union, Callable
from fastapi import FastAPI, Request
import random as rd
from urllib.parse import parse_qs

from baha_utils import BahaCrawler, WebArguments, QueryParams, WAIT_TIME_FN, INF, convert_qs_to_dict

app = FastAPI()  # 建立一個 Fast API application
# page_engine = "selenium"  # VERY SLOW, NOT RECOMMENDED
page_engine = "requests"
crawler = BahaCrawler(page_engine)



@app.get("/")  # 指定 api 路徑 (get方法)
def read_root():
    return {"Hello": "World"}

# baha_urls
@app.get("/baha/urls/default/{baha_query_string}")
def baha_urls_default(baha_query_string: str) -> list:
    query_params_dict = convert_qs_to_dict(QueryParams.BPage, baha_query_string)
    return crawler.get_pages_article_urls(
        web_args_b=WebArguments(query_params=QueryParams.BPage(**query_params_dict))
    )


@app.get("/baha/urls/{crawler_arg_string}/{baha_query_string}")
def baha_urls(crawler_arg_string: str, baha_query_string: str) -> list:
    crawler_arg_dict = convert_qs_to_dict(object, crawler_arg_string)
    query_params_dict = convert_qs_to_dict(object, baha_query_string)
    if("page_type" not in crawler_arg_dict):
        crawler_arg_dict = convert_qs_to_dict(QueryParams.BPage, crawler_arg_string)
        query_params_dict = convert_qs_to_dict(QueryParams.BPage, baha_query_string)
        return crawler.get_pages_article_urls(
            web_args_b=WebArguments(query_params=QueryParams.BPage(**query_params_dict)),
            **crawler_arg_dict,
        )
    
    if(crawler_arg_dict["page_type"]=="searched"):
        crawler_arg_dict = convert_qs_to_dict(QueryParams.SearchPage, crawler_arg_string)
        query_params_dict = convert_qs_to_dict(QueryParams.SearchPage, baha_query_string)
        return crawler.get_pages_article_urls(
            web_args_b=WebArguments(query_params=QueryParams.SearchPage(**query_params_dict)),
            **crawler_arg_dict,
        )
        
    crawler_arg_dict = convert_qs_to_dict(QueryParams.BPage, crawler_arg_string)
    query_params_dict = convert_qs_to_dict(QueryParams.BPage, baha_query_string)
    return crawler.get_pages_article_urls(
            web_args_b=WebArguments(query_params=QueryParams.BPage(**query_params_dict)),
            **crawler_arg_dict,
        )


# baha_article
@app.get("/baha/article/default/{baha_query_string}")
def baha_article_default(baha_query_string: str) -> dict:
    query_params_dict = convert_qs_to_dict(QueryParams.CPage, baha_query_string)
    return crawler.get_article_content(
        web_args_c=WebArguments(query_params=QueryParams.CPage(**query_params_dict))
    )


@app.get("/baha/article/{crawler_arg_string}/{baha_query_string}")
def baha_article(crawler_arg_string: str, baha_query_string: str) -> dict:
    query_params_dict = convert_qs_to_dict(QueryParams.CPage, baha_query_string)
    crawler_arg_dict = convert_qs_to_dict(QueryParams.CPage, crawler_arg_string)
    return crawler.get_article_content(
        web_args_c=WebArguments(query_params=QueryParams.CPage(**query_params_dict)),
        **crawler_arg_dict,
    )

# baha_articles
@app.get("/baha/articles/default/{baha_query_string}")
def baha_articles(baha_query_string: str) -> list:
    query_params_dict = convert_qs_to_dict(QueryParams.BPage, baha_query_string)
    return crawler.get_pages_article_contents(
        web_args_b=WebArguments(query_params=QueryParams.BPage(**query_params_dict)),
    )


@app.get("/baha/articles/{crawler_arg_string}/{baha_query_string}")
def baha_articles(crawler_arg_string: str, baha_query_string: str) -> list:
    query_params_dict = convert_qs_to_dict(object, baha_query_string)
    crawler_arg_dict = convert_qs_to_dict(object, crawler_arg_string)
    if("page_type" not in crawler_arg_dict):
        crawler_arg_dict = convert_qs_to_dict(QueryParams.BPage, crawler_arg_string)
        query_params_dict = convert_qs_to_dict(QueryParams.BPage, baha_query_string)
        return crawler.get_pages_article_contents(
            web_args_b=WebArguments(query_params=QueryParams.BPage(**query_params_dict)),
            **crawler_arg_dict,
        )
    
    if(crawler_arg_dict["page_type"]=="searched"):
        crawler_arg_dict = convert_qs_to_dict(QueryParams.SearchPage, crawler_arg_string)
        query_params_dict = convert_qs_to_dict(QueryParams.SearchPage, baha_query_string)
        return crawler.get_pages_article_contents(
            web_args_b=WebArguments(query_params=QueryParams.SearchPage(**query_params_dict)),
            **crawler_arg_dict,
        )
    
    
    
    query_params_dict = convert_qs_to_dict(QueryParams.BPage, baha_query_string)
    crawler_arg_dict = convert_qs_to_dict(QueryParams.BPage, crawler_arg_string)
    return crawler.get_pages_article_contents(
        web_args_b=WebArguments(query_params=QueryParams.BPage(**query_params_dict)),
        **crawler_arg_dict,
    )
