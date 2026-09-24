"""HTML to clean, traceable evidence conversion."""
from datetime import datetime
import json
import re
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError
from src.models.domain import Evidence, EvidenceType, Source, SourceType
from src.scanner.web_page_scanner import DownloadedPage


class ArticleExtractor:
    """Extract main readable article text without retaining raw HTML."""
    _MIN_WORDS = 100

    def extract(self, page: DownloadedPage, source: Source, scan_run_id: int) -> Evidence:
        """Create evidence from an in-memory HTML page."""
        parsed_url = urlparse(page.url)
        # IFMA's individual-course HTML has malformed menu boundaries. lxml
        # nests the course sections under navigation and cleanup removes them.
        if (parsed_url.hostname == 'www.ifma.org'
                and parsed_url.path.rstrip('/') == '/professional-development/individual-courses'):
            soup = BeautifulSoup(page.html, 'html.parser')
        else:
            soup = BeautifulSoup(page.html, "lxml")
        # ASP.NET pages may wrap the entire main document in a server form.
        # Preserve that content, but do not retain interactive control labels.
        for form in soup.find_all('form'):
            if form.select_one('main, [role="main"]'):
                for control in form.select('input, select, textarea, button'):
                    control.decompose()
                form.unwrap()
        title = (soup.title.string if soup.title and soup.title.string else source.name).strip()
        from src.scanner.nus_curriculum import matches as is_nus_curriculum
        if is_nus_curriculum(page.url):
            curriculum = soup.select_one('#main-container .template-b .col-md-9')
            if curriculum is not None:
                # Preserve complete programme paragraphs and course tables,
                # excluding the neighbouring admissions/faculty sidebar.
                soup = BeautifulSoup(str(curriculum), 'lxml')
        if (parsed_url.hostname == 'www.a-star.edu.sg'
                and unquote(parsed_url.path).lower().rstrip('/') == '/simtech/research/sustainability-informatics-strategy-(sis)'):
            content = soup.select_one('main .rich-text.rte')
            if content is None:
                raise ExtractionError('SIMTech research content block unavailable')
            for unwanted in content.select('script, style, nav, form'):
                unwanted.decompose()
            text = content.get_text('\n', strip=True)
            if len(text.split()) < self._MIN_WORDS:
                raise ExtractionError('Insufficient SIMTech research text')
            return Evidence(None, scan_run_id, source.id or 0, EvidenceType.RESEARCH_CAPABILITY.value,
                            title, self._publication_date(soup), source.organisation, page.url,
                            text, datetime.now().astimezone(), 'EXPLICIT')
        if (parsed_url.hostname == 'www.a-star.edu.sg'
                and parsed_url.path.lower().rstrip('/') in {
                    '/research/medical-technologies',
                    '/research/medical-technologies/innovation-pillars',
                    '/research/medical-technologies/enablers'}):
            body = soup.select_one('section.page-content__inner')
            if body is not None:
                soup = BeautifulSoup(str(body), 'lxml')
        if parsed_url.hostname == 'sgbiodesign.sg':
            # Observed programme-page sections, not phrase-based truncation:
            # keep curriculum text but omit the alumni directory and consent UI.
            for element in soup.select('#meet_the_fellows, #moove_gdpr_cookie_modal, #moove_gdpr_cookie_info_bar'):
                element.decompose()
        # Login destinations can have plausible resource URLs and >100 words.
        # Require both a login-page title and account/access instructions.
        title_lower = title.casefold()
        visible = soup.get_text(' ', strip=True).casefold()
        if (re.match(r'^(member\s+)?(login|log in|sign in)(\s|[-|:]|$)', title_lower)
                and any(marker in visible for marker in ('activate account', 'verification code', 'password', 'login or register'))):
            raise ExtractionError(f'Login page is not public evidence for {source.name}')
        if source.url.rstrip('/') == 'https://www.nasa.gov/reference/systems-engineering-handbook' and soup.find('main'):
            soup = BeautifulSoup(str(soup.find('main')), 'lxml')
        if parsed_url.hostname == 'resourcecenter.ieee-pes.org':
            description = soup.select_one('main article .field--name-body')
            if description is None:
                raise ExtractionError(f'No public resource description for {source.name}')
            for element in description.select('script, style, form, nav'):
                element.decompose()
            text = description.get_text(' ', strip=True)
            if len(text.split()) < self._MIN_WORDS:
                raise ExtractionError(f'Insufficient public resource description for {source.name}')
            # Landing-page descriptions are evidence, not the paid paper/video.
            return Evidence(None, scan_run_id, source.id or 0,
                            EvidenceType.PROFESSIONAL_RESOURCE.value,
                            title + ' [Public resource description]',
                            self._publication_date(soup), source.organisation, page.url,
                            'Public resource description only; full resource not retrieved.\n\n' + text,
                            datetime.now().astimezone(), 'INFERRED')
        if source.source_type == SourceType.FRAMEWORK:
            return self._extract_framework_evidence(soup, page, source, scan_run_id, title)
        if source.source_type == SourceType.CATALOGUE:
            return self._extract_catalogue_evidence(soup, page, source, scan_run_id, title)
        if self._looks_like_issue_hub(title, soup):
            raise ExtractionError(f"Skipping issue hub for {source.name}")
        structured = self._extract_structured_article(soup)
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
            element.decompose()
        article = soup.find("article") or soup.find("main") or soup.body
        text = structured or self._extract_article_text(article)
        paragraph_text = self._extract_dense_paragraph_text(soup)
        if len(paragraph_text) > len(text):
            text = paragraph_text
        if len(text.split()) < self._MIN_WORDS:
            raise ExtractionError(f"Insufficient article text for {source.name}")
        evidence_type = self._classify_evidence_type(source).value
        explicit_or_inferred = "EXPLICIT" if source.source_type == SourceType.FRAMEWORK else "INFERRED"
        date_tag = soup.find("time")
        metadata_date = (
            soup.find("meta", attrs={"property": "article:published_time"})
            or soup.find("meta", attrs={"name": "publication_date"})
            or soup.find("meta", attrs={"name": "date"})
            or soup.find("meta", attrs={"itemprop": "datePublished"})
            or soup.find("meta", attrs={"property": "og:updated_time"})
        )
        publication_date = date_tag.get("datetime") if date_tag and date_tag.get("datetime") else metadata_date.get("content") if metadata_date and metadata_date.get("content") else None
        return Evidence(None, scan_run_id, source.id or 0, evidence_type, title, publication_date, source.organisation, page.url, text, datetime.now().astimezone(), explicit_or_inferred)

    def _extract_framework_evidence(self, soup: BeautifulSoup, page: DownloadedPage, source: Source, scan_run_id: int, title: str) -> Evidence:
        """Preserve visible hierarchy for explicit competency/framework pages."""
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
            element.decompose()
        text = self._extract_hierarchy_text(soup)
        if len(text.split()) < 8:
            raise ExtractionError(f"Insufficient framework text for {source.name}")
        publication_date = self._publication_date(soup)
        framework_title = title or source.name
        return Evidence(None, scan_run_id, source.id or 0, EvidenceType.EXPLICIT_COMPETENCY.value, framework_title, publication_date, source.organisation, page.url, text, datetime.now().astimezone(), "EXPLICIT")

    def _extract_catalogue_evidence(self, soup: BeautifulSoup, page: DownloadedPage, source: Source, scan_run_id: int, title: str) -> Evidence:
        """Preserve repeated catalogue records where courses/programmes are listed."""
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
            element.decompose()
        text = self._extract_catalogue_text(soup)
        if len(text.split()) < 8:
            raise ExtractionError(f"Insufficient catalogue text for {source.name}")
        if self._is_short_catalogue_utility(title, text):
            raise ExtractionError(f"Navigation-only catalogue content for {source.name}")
        publication_date = self._publication_date(soup)
        return Evidence(None, scan_run_id, source.id or 0, EvidenceType.PROFESSIONAL_RESOURCE.value, title, publication_date, source.organisation, page.url, text, datetime.now().astimezone(), "INFERRED")

    @staticmethod
    def _is_short_catalogue_utility(title: str, text: str) -> bool:
        """Reject known utility-only shapes, not concise academic records."""
        if len(text.split()) >= 100:
            return False
        if title.strip().casefold() == 'chat with a student':
            return True
        # An invitation to browse a catalogue is not the catalogue itself.
        blocks = [re.sub(r'\s+', ' ', block).strip().casefold()
                  for block in text.split('\n\n') if block.strip()]
        navigation = {
            'undergraduate programme', 'resources', 'explore our resources',
            'academic calendar', 'sutd courses',
            'get more details about your school terms, vacation periods and more.',
            'browse courses offered throughout sutd, and discover the best fit for your interests.',
        }
        return (len(blocks) >= 3 and 'academic calendar' in blocks
                and all(block in navigation for block in blocks))

    @staticmethod
    def _classify_evidence_type(source: Source) -> EvidenceType:
        label = (source.evidence_label or "news / commentary").lower()
        if "framework" in label or source.source_type == SourceType.FRAMEWORK:
            return EvidenceType.EXPLICIT_COMPETENCY
        if "catalogue" in label or "training" in label or source.source_type == SourceType.CATALOGUE:
            return EvidenceType.PROFESSIONAL_RESOURCE
        if source.source_type == SourceType.RESEARCH or "research" in label or "report" in label:
            return EvidenceType.RESEARCH_CAPABILITY
        if "standard" in label or "guidance" in label:
            return EvidenceType.EXPLICIT_COMPETENCY
        if "trend" in label:
            return EvidenceType.TREND_SIGNAL
        return EvidenceType.ARTICLE_TEXT

    @staticmethod
    def _looks_like_issue_hub(title: str, soup: BeautifulSoup) -> bool:
        title_text = title.lower()
        if re.search(r"^[a-z]+\s+\d{4}\s*-\s*ieee spectrum$", title_text):
            return True
        body_text = soup.get_text(" ", strip=True).lower()
        return "in this issue:" in body_text and "see full issue" in body_text

    @staticmethod
    def _extract_structured_article(soup: BeautifulSoup) -> str:
        scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        for script in scripts:
            raw = script.string or script.get_text(strip=True)
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            nodes = payload if isinstance(payload, list) else [payload]
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                if isinstance(node.get("@graph"), list):
                    for graph_item in node["@graph"]:
                        if isinstance(graph_item, dict):
                            article_body = graph_item.get("articleBody")
                            if isinstance(article_body, str) and len(article_body.strip()) >= 50:
                                return article_body.strip()
                article_body = node.get("articleBody")
                if isinstance(article_body, str) and len(article_body.strip()) >= 50:
                    return article_body.strip()
        return ""

    @staticmethod
    def _extract_article_text(article) -> str:
        if article is None:
            return ""
        blocks: list[str] = []
        for element in article.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote"], recursive=True):
            text = element.get_text(" ", strip=True)
            if text:
                blocks.append(text)
        if blocks:
            cleaned: list[str] = []
            for block in blocks:
                if cleaned and block == cleaned[-1]:
                    continue
                cleaned.append(block)
            return "\n\n".join(cleaned)
        return article.get_text("\n\n", strip=True)

    @staticmethod
    def _extract_dense_paragraph_text(soup: BeautifulSoup) -> str:
        candidates: list[str] = []
        for container in soup.find_all(["article", "main", "section", "div"]):
            paragraphs = [node.get_text(" ", strip=True) for node in container.find_all("p")]
            paragraphs = [text for text in paragraphs if len(text) >= 40]
            if len(paragraphs) >= 3:
                candidate = "\n\n".join(paragraphs)
                candidates.append(candidate)
        if candidates:
            candidates.sort(key=len, reverse=True)
            return candidates[0]
        paragraphs = [node.get_text(" ", strip=True) for node in soup.find_all("p")]
        paragraphs = [text for text in paragraphs if len(text) >= 40]
        return "\n\n".join(paragraphs)

    @staticmethod
    def _extract_hierarchy_text(soup: BeautifulSoup) -> str:
        blocks: list[str] = []
        for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "li", "p", "table", "tr"]):
            text = element.get_text(" ", strip=True)
            if text:
                blocks.append(text)
        deduped: list[str] = []
        for block in blocks:
            if block not in deduped:
                deduped.append(block)
        return "\n\n".join(deduped)

    @staticmethod
    def _extract_catalogue_text(soup: BeautifulSoup) -> str:
        # Read actual curriculum content in document order. Card summaries below
        # used to truncate records to six parts and replace course names with URLs.
        content = soup.select_one("main, [role='main'], #content") or soup
        expanded = content.select_one('#expanded-description')
        collapsed = content.select_one('#collapsed-description')
        if expanded and expanded.get_text(strip=True) and collapsed:
            collapsed.decompose()
        for unwanted in content.select("nav, footer, header, [role='navigation'], .printoptions, #printoptions"):
            unwanted.decompose()
        blocks = []
        # Definition lists carry full syllabuses on some university pages;
        # legacy centre blocks may contain course availability notices.
        selected = content.select('h1, h2, h3, h4, h5, h6, p, li, tr, dt, dd, center, div.card__body, .course-info-content, #expanded-description')
        selected_ids = {id(element) for element in selected}
        for element in selected:
            if any(id(parent) in selected_ids for parent in element.parents):
                continue
            text = element.get_text(" ", strip=True)
            if text and text not in blocks:
                blocks.append(text)
        if blocks:
            return "\n\n".join(blocks)
        records: list[str] = []
        for card in soup.find_all(["article", "li", "section", "div"]):
            heading = card.find(["h1", "h2", "h3", "h4", "h5", "h6"])
            paragraphs = [p.get_text(" ", strip=True) for p in card.find_all("p")]
            links = [a.get("href") for a in card.find_all("a", href=True)]
            parts = []
            if heading and heading.get_text(" ", strip=True):
                parts.append(heading.get_text(" ", strip=True))
            parts.extend([p for p in paragraphs if p])
            parts.extend([link for link in links if link])
            if parts:
                record = " | ".join(parts[:6])
                if record not in records:
                    records.append(record)
        if records:
            return "\n\n".join(records)
        return ArticleExtractor._extract_dense_paragraph_text(soup)

    @staticmethod
    def _publication_date(soup: BeautifulSoup) -> str | None:
        date_tag = soup.find("time")
        metadata_date = (
            soup.find("meta", attrs={"property": "article:published_time"})
            or soup.find("meta", attrs={"name": "publication_date"})
            or soup.find("meta", attrs={"name": "date"})
            or soup.find("meta", attrs={"itemprop": "datePublished"})
            or soup.find("meta", attrs={"property": "og:updated_time"})
        )
        return date_tag.get("datetime") if date_tag and date_tag.get("datetime") else metadata_date.get("content") if metadata_date and metadata_date.get("content") else None
