"""Coarse HTML diagnostics without exposing page text, tokens or incident IDs."""
from bs4 import BeautifulSoup


def html_diagnostics(html):
    soup = BeautifulSoup(html, 'lxml')
    scripts = len(soup.find_all('script'))
    main = bool(soup.select_one('main, [role="main"]'))
    for node in soup.select('script, style, head, template'):
        node.decompose()
    text = soup.get_text(' ', strip=True).casefold()
    markers = ('access denied', 'request unsuccessful', 'incapsula incident id',
               'verify you are human', 'checking your browser', 'enable javascript and cookies')
    access_hint = any(marker in text for marker in markers)
    return (f'HTML bytes={len(html.encode("utf-8"))}; visible words={len(text.split())}; '
            f'main present={main}; scripts={scripts}; access-notice hint={access_hint}. '
            'These are diagnostic hints, not proof of the cause; no response text is included.')
