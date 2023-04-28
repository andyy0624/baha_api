from urllib.parse import urlencode, urlparse

class UrlBuilder():
    def __init__(self, url: str) -> None:
        self._url = url
        self._base_url, self._params = self._parse_url()
        
    def __call__(self, *args, **kwargs) -> str:
        args_dict = dict([arg.split("=") for arg in args])
        kwargs_dict = kwargs
        params = {**self._params, **args_dict, **kwargs_dict}
        query_string = urlencode(params)
        return f"{self._base_url}?{query_string}"
    def _parse_url(self) -> tuple:
        parsed_url = urlparse(self._url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        param_dict = dict([x.split('=') for x in parsed_url.query.split('&')]) if parsed_url.query != "" else {}
        return base_url, param_dict

if __name__ == "__main__":
    baha_url = "https://forum.gamer.com.tw"+"/B.php"
    bsn = "bsn=60030"
    baha_url_builder = UrlBuilder(baha_url)
    baha_url_builder(bsn, page=2)
    
    baha_url_builder(bsn="60030", page=2)
    
    url = "https://forum.gamer.com.tw/C.php?bsn=60030&snA=623425&page=2"
    a = urlparse(url)
    b = urlparse(url).query.split('&')
    dict([x.split('=') for x in urlparse(url).query.split('&')])
    f"{a.scheme}://{a.netloc}{a.path}"
    
    baha_url_builder = UrlBuilder(url)
    baha_url_builder(bsn=23997)
    "".split('&')
    baha_url_builder._parse_url()
    