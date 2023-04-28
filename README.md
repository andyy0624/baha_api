# baha_api

#### FastAPI啟動方法
```console
uvicorn main:app --reload
```

#### swagger-ui API文件
```url
127.0.0.1:8000/docs
```

#### 取得巴哈某版文章列表中的文章網址
以每頁為單位，每頁共30筆。以下範例為巴哈電腦應用版（bsn=60030），1-5頁的所有文章網址
```url
127.0.0.1:8000/baha/get_article_urls_pages?bsn=60030&page_start=1&page_end=5
```

#### 取得巴哈某版某文章的所有貼文資訊
包含整個貼文串（每層樓）的所有內容。以下範例為巴哈電腦應用版，snA編號623838文章的所有內容
```url
127.0.0.1:8000/baha//baha/get_article_contents?bsn=60030&snA=623838
```
