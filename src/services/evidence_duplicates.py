"""Conservative identities for content-reviewed duplicate public resources."""
from hashlib import sha256
from urllib.parse import urlparse


def public_description_key(evidence):
    parsed = urlparse(evidence.url)
    text = getattr(evidence, 'article_text', '')
    if (parsed.scheme == 'https' and parsed.hostname == 'www.sutd.edu.sg'
            and parsed.path.rstrip('/') == '/esd/education/undergraduate/courses' and text.strip()):
        digest = sha256(' '.join(text.split()).encode('utf-8')).hexdigest()
        return (evidence.organisation, parsed.hostname + parsed.path.rstrip('/'), parsed.query, digest)
    if (parsed.hostname != 'resourcecenter.ieee-pes.org'
            or not parsed.path.startswith('/education/webinars/')
            or not text.startswith('Public resource description only; full resource not retrieved.')):
        return None
    # The observed _sld suffix identifies the slide landing page for the same
    # webinar. Do not merge different webinar IDs sharing boilerplate text.
    path = parsed.path.rstrip('/')
    if path.endswith('_sld'):
        path = path[:-4]
    digest = sha256(' '.join(text.split()).encode('utf-8')).hexdigest()
    return (evidence.organisation, path, parsed.query, digest)
