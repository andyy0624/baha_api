# baha_api

## 說明

* **支援取得文章(Article)、回覆(Reply)、留言(Comment)**：將巴哈論壇頁面上的資訊，以json格式回傳。以每板的板編bsn、文章編號snA作為GET parameters(or query strings)來取得巴哈文章(Article)，以每頁樓數(10樓)單位，取得該貼文的所有回覆(Reply)，並取得每則回覆的留言(Comment)。

* **可選用selenium取得完整留言**：載入頁面的引擎可選用requests or selenium，載入文章列表的引擎已永遠綁定使用requests，以提升效能；載入文章頁面的引擎則可選用selenium。僅採用selenium引擎情況下才有辦法爬取所有留言，否則一般只取得頁面上巴哈預設載入的留言。

* **選用與自己瀏覽器匹配的chromedriver**：若要採用selenium引擎，請自行下載chromedriver，選用與自己瀏覽器相匹配的版本。

* **完整抓取留言**：當採用selenium引擎開啟文章頁面時，將會模擬使用者展開所有留言，並檢查所有留言是否已載入完畢，遂進行頁面內容的抓取，以確保沒有留言內容遺失。

* **謹慎選用**：採用selenium引擎的執行速度約只有requests的1/10，請謹慎選用。

* **保留多種URL連結**：抓取文本內容時，保留了存在於文章中的「圖片連結」、「超連結」以及「巴哈Emoji」等URL連結，而非僅有完全的文字內容。

* **採遞迴方法取得內容**：以遞迴方法取得文字、圖片連結等內容，以保留連結在文章中的順序關係

## 遞迴方法取得內容

```python
# 遞迴方法取得文字、圖片連結等內容，以保留連結在文章中的順序關係
def extract_text_dfs(elements, result_text: list):
    if not isinstance(elements, Tag):
        result_text += [elements]
        return

    # leaf element
    if not elements.find_all(recursive=False):
        # image
        if elements.name == "img" and elements.has_attr("data-src"):
            img_data = {"image": elements.get("data-src")}
            result_text += [json.dumps(img_data)]
        # emotion
        if (
            elements.name == "img"
            and elements.has_attr("src")
            and elements.has_attr("border")
        ):
            img_data = {"emotion": elements.get("src")}
            result_text += [json.dumps(img_data)]
        # hyperlink
        if (
            elements.name == "a"
            and elements.has_attr("href")
            and elements.has_attr("target")
            and elements["target"] == "_blank"
        ):
            hyperlink_data = {
                "hyperlink": elements.get("href"),
                "text": elements.text,
            }
            result_text += [json.dumps(hyperlink_data)]
        result_text += [elements.text]
        return

    for element in elements.contents:
        extract_text_dfs(element, result_text)
```

## 輸出範例(page_engine='requests')

```json
// 輸出範例
{
  "title": "【攻略】2021 144Hz ⬆ 高刷新螢幕規格整理/挑選指南/集中討論帖",
  "url": "https://forum.gamer.com.tw/C.php?bsn=60030&snA=457957",
  "reply": [
    {
      "reply_id": "post_2015250",
      "user_id": "west3456",
      "user_name": "starmoonall",
      "content": "\n {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=https%3A%2F%2Fsites.google.com%2Fview%2Ftwmonitors%2F%E9%A6%96%E9%A0%81\", \"text\": \"星河電腦螢幕資訊分享站\"} 星河電腦螢幕資訊分享站 (Google site) ⬆⬆⬆ 歡迎進入個人網站查看螢幕規格表格與相關知識 ⬆⬆⬆ (加入書籤能更方便) <   討論串切換門   > |  144Hz 螢幕討論串  |  21:9 螢幕討論串  |  4K UHD 螢幕討論串  |  2K 典型螢幕討論串  | 螢幕目前分為五大類, 144Hz  /  21:9  /  4K  /  2K   (60Hz) /  FHD  (60Hz) *想要什麼樣規格的產品, 請到對應的帖進行討論交流. ( FHD 60Hz直接發新文章問就好了 ) {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=https%3A%2F%2Fsites.google.com%2Fview%2Ftwmonitors%2F%E5%B9%B4%E5%BA%A6%E5%A4%A7%E8%B3%9E%2F2020%E7%B8%BD%E8%A9%95%E8%A1%A8%E4%B8%8D%E5%AE%9A%E6%9C%9F%E6%9B%B4%E6%96%B0\", \"text\": \"2020 總評表 (不定期更新)\"} 2020 總評表 (不定期更新)  <- 連結 這是網站中 最重要的頁面 , 個人對當下較出色產品進行排序的總評表, 這就很夠花時間參考研究了. 想自行研究螢幕產品, 個人還有整理這兩個基本帖,  也可參考. 【心得】挑選螢幕流程指南, 必懂基本要素整理. {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=https%3A%2F%2Fforum.gamer.com.tw%2FC.php%3Fbsn%3D60030%26snA%3D488050\", \"text\": \"【心得】自行研究各型號螢幕最正確評價基準&方法整理\"} 【心得】自行研究各型號螢幕最正確評價基準&方法整理 購買螢幕不確定是否可以達自己期望值， 請 到實體店面進行 實機確認 後再行購買, 或 利用 有 7天鑑賞期之網路商店 ， 7天內發現螢幕有壞點或是不適合都可以有理由退。 (有漏有錯也請在文章註明, 看到的話會更新) 新品開賣也請提醒本人做更新 , 謝謝了! 以下為個人比較印象深刻的好用網站 \n \n Display Specifications \n 螢幕規格整理權威網站(個人最常用) \n \n \n Productchart \n 利用規格篩選螢幕 - 天梯系統 \n \n \n Display LAG \n 型號+INPUT LAG輸入延遲查詢系統 \n \n \n {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=http%3A%2F%2Fwww.144hzmonitors.com%2Fgaming-monitor-list-120hz-144hz-165hz-200hz-240hz%2F\", \"text\": \"1\"} 1 {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=http%3A%2F%2Fwww.144hzmonitors.com%2Fgaming-monitor-list-120hz-144hz-165hz-200hz-240hz%2F\", \"text\": \"44hzmonitors\"} 44hzmonitors  /  {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=http%3A%2F%2Fwww.blurbusters.com%2Ffaq%2F120hz-monitors%2F\", \"text\": \"Blurbusters\"} Blurbusters \n 120~240hz螢幕型號清單 \n \n \n {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=http%3A%2F%2Fwww.144hzmonitors.com%2Flist-of-g-sync-monitors%2F\", \"text\": \"144hzmonitors\"} 144hzmonitors  /  {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=http%3A%2F%2Fwww.blurbusters.com%2Fgsync%2Flist-of-gsync-monitors%2F\", \"text\": \"Blurbusters\"} Blurbusters  /  {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FNvidia_G-Sync\", \"text\": \"Wiki\"} Wiki \n Gsync螢幕清單 \n \n \n TFTcentral Panel Datebase \n 市場上各種尺寸大小\"面板\"規格整理 \n \n \n Panelook \n 面板詳細規格查詢網站 \n \n \n {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FDisplayPort\", \"text\": \"Displayport\"} Displayport  /  {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FHDMI\", \"text\": \"HDMI\"} HDMI \n 輸出端子版本 對應解析度+HZ支援度查詢表格 \n \n \n {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=http%3A%2F%2Fbigboy2000.blogspot.tw%2F2009%2F12%2Fdiagonal-size-conversion.html\", \"text\": \"螢幕尺寸換算 (對角線尺寸簡易換算)\"} 螢幕尺寸換算 (對角線尺寸簡易換算) {\"hyperlink\": \"https://ref.gamer.com.tw/redir.php?url=http%3A%2F%2Fbigboy2000.blogspot.tw%2F2009%2F12%2Fdiagonal-size-conversion.html\", \"text\": \"by大男孩\"} by大男孩 \n 輸入螢幕尺寸算出實際寬與高 \n \n 轉載在其他網站分享, 尊重智產權, 請註明本人作品. {\"image\": \"https://truth.bahamut.com.tw/s01/201807/7e01a0ecffa1a729156cff6e6e21bf28.PNG\"} \n",
      "floor": 1,
      "publish_time": "2017-03-29T19:19:45",
      "gp_count": 706,
      "bp_count": 25,
      "comments": [
        {},
        {
          "comment_id": "Commendcontent_3360023",
          "user_id": "ty028473",
          "user_name": "我是狗汪汪",
          "content": "[tocosusi:路人甲乙丙丁]那你應該是買電視 會比較爽",
          "floor": "B487",
          "publish_time": "2022-12-09T16:25:50",
          "gp_count": 0,
          "bp_count": 0
        },
        {
          "comment_id": "Commendcontent_3392119",
          "user_id": "daisiusiu",
          "user_name": "daisiusiu",
          "content": "路人甲乙丙丁 Oled 幫到你",
          "floor": "B488",
          "publish_time": "2023-01-23T16:18:29",
          "gp_count": 0,
          "bp_count": 0
        },
        {
          "comment_id": "Commendcontent_3395342",
          "user_id": "EvAn0227",
          "user_name": "鋼鐵韓粉",
          "content": "請問27吋 2k螢幕中畫質最好的是哪台啊",
          "floor": "B489",
          "publish_time": "2023-01-30T09:36:24",
          "gp_count": 0,
          "bp_count": 0
        },
        {
          "comment_id": "Commendcontent_3410098",
          "user_id": "zzxcv5432",
          "user_name": "メリイ",
          "content": "都限定2k畫質了，不是都一樣嗎？",
          "floor": "B490",
          "publish_time": "2023-02-23T06:43:56",
          "gp_count": 0,
          "bp_count": 0
        }
      ]
    }
  ]
}
```

## FastAPI啟動方法

```console
uvicorn main:app --reload
```

## swagger-ui API文件

```url
127.0.0.1:8000/docs
```

## 修改main.py中的page_engine來使用selenium作為頁面引擎

```python
# main.py
page_engine = "selenium" # VERY SLOW, NOT RECOMMENDED
```

## 取得巴哈某版文章列表中的文章網址

以每頁為單位，每頁共30筆，取得文章列表中的文章網址。以下範例為巴哈電腦應用版（bsn=60030），1-5頁的所有文章網址

```url
127.0.0.1:8000/baha/get_article_urls_pages?bsn=60030&page_start=1&page_end=5
```

## 取得巴哈某版某文章的所有回覆及留言內容

以每頁樓數為單位，每頁共10樓，自動取得總頁數, 取得包含文章所有回覆（每層樓）的所有內容。以下範例為巴哈電腦應用版（bsn=60030），snA編號623838文章的所有內容

```url
127.0.0.1:8000/baha/get_article_contents?bsn=60030&snA=623838
```

## 取得巴哈某版從文章列表A頁到B頁的所有回覆及留言內容

取得從start_page開始，到end_page結束的所有文章內容。以下範例為巴哈電腦應用版（bsn=60030），文章列表1-2頁且限制只爬取5頁文章回覆的所有文章內容

```url
127.0.0.1:8000/baha/get_pages_article_contents?bsn=60030&start_page=1&end_page=2&limit_subPage=5
```
