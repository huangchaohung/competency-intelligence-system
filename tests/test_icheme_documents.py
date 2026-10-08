from types import SimpleNamespace
from dataclasses import replace
from src.models.domain import Source
from src.scanner.source_router import SourceRouter


def test_reviewed_documents_include_learning_outcomes_not_navigation():
    root = 'https://www.icheme.org/knowledge-networks/knowledge-resources/safety-centre/framework/knowledge-and-competence'
    paths = ['/media/12452/0007_18-competency_brochure-update.pdf',
             '/media/16241/competency-guidance-supplementary-guide.pdf',
             '/media/14927/0008_18-learning_outcomes_brochure-final.pdf']
    html = ''.join(f'<a href="{p}">Learning Outcomes</a>' for p in paths + [paths[0], '/knowledge-networks/'])
    scanner = SimpleNamespace(is_allowed=lambda u: True,
                              fetch_url=lambda *a: SimpleNamespace(url=root, html=html))
    source = Source(1, 'IChemE', root, 'IChemE', max_articles_per_scan=25)
    assert SourceRouter(scanner).discover(source) == ['https://www.icheme.org'+p for p in paths]
    source = replace(source, max_articles_per_scan=1)
    assert len(SourceRouter(scanner).discover(source)) == 1
