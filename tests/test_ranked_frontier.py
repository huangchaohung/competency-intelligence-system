from src.scanner.competency_pilot import search_trap, frontier_score, qualification, js_shell


def test_search_and_facets_excluded_but_course_query_preserved():
    assert search_trap('https://example.org/search?q=engineering')
    assert search_trap('https://example.org/courses?filter=all')
    assert not search_trap('https://example.org/course?id=123')


def test_rank_substance_above_homepage():
    assert frontier_score('https://example.org/engineering/modules/control') > frontier_score('https://example.org/')


def test_body_outcomes_can_qualify_without_matching_heading():
    assert qualification('https://example.org/detail/123', 'Control design', 'Overview', [
        'On completion of this course students will apply engineering control methods and evaluate technical requirements.'
    ])[0]
    assert not qualification('https://example.org/detail/123', 'Control design', 'Overview', [
        'Our engineering department welcomes visitors to its modern buildings and facilities.'
    ])[0]


def test_browser_only_for_sparse_js_shell():
    result = ('https://example.org', b'<html><div id="root"></div></html>', 'text/html', {})
    assert js_shell(result, ('', '', [], []))
    assert not js_shell(result, ('', '', ['real content ' * 100], []))
    assert not js_shell(None, None)
