from types import SimpleNamespace
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source


def test_structured_zju_urls_are_scoped_deduplicated_and_capped():
    root = 'https://www.zju.edu.cn/english/sustainability/main.htm'
    path = '/english/2023/0904/c65143a2797393/page.psp'
    html = ''.join('<span class="url">'+u+'</span>' for u in [path,path,'https://other.example'+path,'/english/main.htm','/_upload/report.pdf'])
    scanner = SimpleNamespace(is_allowed=lambda u: True, fetch_url=lambda *a: DownloadedPage(root,html))
    assert SourceRouter(scanner).discover(Source(1,'ZJU',root,'ZJU',max_articles_per_scan=1)) == ['https://www.zju.edu.cn'+path]
