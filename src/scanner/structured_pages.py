"""Reviewed standalone competency and curriculum overviews."""
from urllib.parse import urlparse


def body_selector(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https':
        return None
    if (parsed.hostname in {'www.ice.org.uk', 'ice.org.uk'} and
            parsed.path.rstrip('/') == '/join-ice/attributes-for-professionally-qualified-membership'):
        return 'main.main-landing .accordion-tabs'
    if (parsed.hostname == 'sust.hkust.edu.hk' and
            parsed.path.rstrip('/') == '/students/sustainability-education'):
        return 'main article.node'
    return None
