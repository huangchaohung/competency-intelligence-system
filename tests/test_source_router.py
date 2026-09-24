from src.models.domain import Source, SourceRole, SourceType
from src.scanner.source_router import SourceRouter
from dataclasses import replace


class FakeDiscovery:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def discover_index(self, source: Source) -> list[str]:
        self.calls.append("index")
        return ["index"]

    def discover_trend(self, source: Source) -> list[str]:
        self.calls.append("trend")
        return ["trend"]

    def discover_resources(self, source: Source) -> list[str]:
        self.calls.append("resources")
        return ["resources"]

    def discover(self, source: Source) -> list[str]:
        self.calls.append("generic")
        return ["generic"]


class FakeScanner:
    pass


def _source(source_type: SourceType) -> Source:
    return Source(
        None,
        "Test",
        "https://example.org/news",
        "Example Org",
        "Singapore",
        True,
        "Uncategorised",
        10,
        "",
        True,
        3,
        False,
        "news / commentary",
        source_type,
        SourceRole.PRIMARY_DISCOVERY,
        True,
    )


def test_trend_sources_use_trend_discovery_path(monkeypatch) -> None:
    router = SourceRouter(FakeScanner())
    fake = FakeDiscovery()
    monkeypatch.setattr(router, "_discovery", fake)

    assert router.discover(_source(SourceType.TREND)) == ["trend"]
    assert fake.calls == ["trend"]


def test_index_sources_use_index_discovery_path(monkeypatch) -> None:
    router = SourceRouter(FakeScanner())
    fake = FakeDiscovery()
    monkeypatch.setattr(router, "_discovery", fake)

    assert router.discover(_source(SourceType.INDEX)) == ["index"]
    assert fake.calls == ["index"]


def test_framework_and_catalogue_sources_use_resource_discovery_path(monkeypatch) -> None:
    router = SourceRouter(FakeScanner())
    fake = FakeDiscovery()
    monkeypatch.setattr(router, "_discovery", fake)

    assert router.discover(_source(SourceType.FRAMEWORK)) == ["resources"]
    assert router.discover(_source(SourceType.CATALOGUE)) == ["resources"]
    assert fake.calls == ["resources", "resources"]


def test_other_sources_use_generic_discovery_path(monkeypatch) -> None:
    router = SourceRouter(FakeScanner())
    fake = FakeDiscovery()
    monkeypatch.setattr(router, "_discovery", fake)

    assert router.discover(_source(SourceType.ARTICLE)) == ["generic"]
    assert fake.calls == ["generic"]


def test_configured_research_resource_includes_resource_discovery(monkeypatch) -> None:
    router = SourceRouter(FakeScanner())
    fake = FakeDiscovery()
    monkeypatch.setattr(router, '_discovery', fake)
    source = replace(_source(SourceType.ARTICLE), evidence_label='research / report')
    assert router.discover(source) == ['resources']
    assert source.source_type == SourceType.ARTICLE


def test_research_label_does_not_override_explicit_trend_route(monkeypatch) -> None:
    router = SourceRouter(FakeScanner())
    fake = FakeDiscovery()
    monkeypatch.setattr(router, '_discovery', fake)
    assert router.discover(replace(_source(SourceType.TREND), evidence_label='research / report')) == ['trend']
def test_ocw_cards_only_admit_bounded_permitted_ste_courses():
    from src.scanner.source_router import SourceRouter
    from src.scanner.web_page_scanner import DownloadedPage
    from src.models.domain import Source
    class Scanner:
        def is_allowed(self, url):
            return 'blocked' not in url
        def fetch_url(self, url, name):
            cards = [('Science', '/courses/physics/'), ('Science', '/courses/physics/'),
                     ('Humanities', '/courses/history/'), ('Engineering', '/courses/blocked/'),
                     ('Engineering', 'https://other.example/courses/test/')]
            return DownloadedPage(url, ''.join(f'<div class="course-card"><div class="course-card-topics"><a>{topic}</a></div><div class="course-card-title"><a href="{href}">Course</a></div></div>' for topic, href in cards))
    assert SourceRouter(Scanner()).discover(Source(1, 'OCW', 'https://ocw.mit.edu/', 'MIT', max_articles_per_scan=1)) == ['https://ocw.mit.edu/courses/physics/']
    assert SourceRouter(Scanner()).discover(Source(1, 'OCW', 'https://ocw.mit.edu/', 'MIT')) == ['https://ocw.mit.edu/courses/physics/']
