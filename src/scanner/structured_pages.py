"""Reviewed standalone competency and curriculum overviews."""
from urllib.parse import urlparse


def body_selector(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https':
        return None
    if (parsed.hostname in {'www.ice.org.uk', 'ice.org.uk'} and
            parsed.path.rstrip('/') in {'/attributes', '/join-ice/attributes-for-professionally-qualified-membership'}):
        return 'main.main-landing .accordion-tabs'
    if (parsed.hostname == 'www.a-star.edu.sg' and
            parsed.path.rstrip('/') == '/simtech/kto/industrial-automation'):
        return 'main .rich-text.rte.block'
    if (parsed.hostname == 'sust.hkust.edu.hk' and
            parsed.path.rstrip('/') == '/students/sustainability-education'):
        return 'main article.node'
    if (parsed.hostname == 'www.polimi.it' and parsed.path.rstrip('/') in {
            '/en/education/laurea-programmes/programme-detail/building-engineering-for-sustainability',
            '/en/education/laurea-magistrale-programmes/programme-detail/civil-engineering'}):
        return 'main#page-content'
    return None
