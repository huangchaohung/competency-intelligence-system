"""Source configuration page."""
from dataclasses import replace
import pandas as pd
import streamlit as st
from src.core.exceptions import ConfigurationError
from src.models.domain import Source, SourceFamily, SourceRole, SourceType
from src.services.source_catalogue_export import sources_csv


def _type_badge(source_type: SourceType) -> str:
    if source_type == SourceType.FRAMEWORK:
        return "🟢 framework"
    if source_type == SourceType.CATALOGUE:
        return "🔵 catalogue"
    if source_type == SourceType.INDEX:
        return "🟣 index"
    if source_type == SourceType.TREND:
        return "🟠 trend"
    return "⚪ article"


def _type_description(source_type: SourceType) -> str:
    if source_type == SourceType.FRAMEWORK:
        return "Authoritative competency structures or standards documents."
    if source_type == SourceType.CATALOGUE:
        return "Curated resource lists, training catalogues, or content libraries."
    if source_type == SourceType.INDEX:
        return "Hub pages that point to deeper pages within the same site."
    if source_type == SourceType.TREND:
        return "News or topic streams used to spot emerging themes."
    return "Standalone article pages with one primary item of evidence."


def _family_badge(source_family: SourceFamily) -> str:
    if source_family == SourceFamily.PROFESSIONAL_BODY:
        return "🟢 professional bodies"
    if source_family == SourceFamily.HIGHER_LEARNING:
        return "🔵 higher learning"
    return "🟣 government agencies"


def _family_description(source_family: SourceFamily) -> str:
    if source_family == SourceFamily.PROFESSIONAL_BODY:
        return "Professional bodies and societies publishing competency frameworks, standards, and courses."
    if source_family == SourceFamily.HIGHER_LEARNING:
        return "Universities and tertiary institutions publishing courses, research, and capability programmes."
    return "Government agencies publishing public guidance, programmes, roadmaps, and research initiatives."


def render(services: dict) -> None:
    """Render a validated, officer-controlled source catalogue editor."""
    st.header("Source Configuration")
    sources = services["source_repository"].list_all()
    enabled_sources = [source for source in sources if source.enabled]
    st.info("Colour guide: 🟢 professional bodies; 🔵 higher learning; 🟣 government agencies.")
    _render_catalogue_exports(sources, enabled_sources)
    _render_grouped_enabled_sources(services, enabled_sources)
    st.markdown("---")
    st.subheader("Catalogue operations")
    st.caption("Use these controls to make changes to the source catalogue. They are separate from the approved source list above.")
    with st.expander("Edit Sources"):
        _render_bulk_editor(services, sources)


def _render_catalogue_exports(sources: list[Source], enabled_sources: list[Source]) -> None:
    """Render compact source catalogue export controls."""
    left, middle, right = st.columns(3)
    left.download_button(
        "Download enabled sources (CSV)",
        data=sources_csv(enabled_sources),
        file_name="enabled_sources.csv",
        mime="text/csv",
    )


def _render_bulk_editor(services: dict, sources: list[Source]) -> None:
    st.info(
        "**Add or edit:** Enter a source in the blank row at the bottom, or click an existing cell to change it.\n\n"
        "**Delete:** Hover over the far-left edge of a row, select it using the row-selection control, "
        "then click the trash/bin icon in the table toolbar. Unticking Enabled only stops scanning; "
        "it does not select or delete the row. Past evidence is kept when a source is removed.\n\n"
        "**Validate and save:** Changes remain a draft until you click Validate catalogue changes, "
        "review the changes, confirm any removals, and click Apply validated changes. "
        "Use Discard draft after validation if you do not want to save them."
    )
    table = pd.DataFrame([{"_key": _row_key(source, index), "Enabled": source.enabled, "Browser": source.use_browser_rendering, "Country": source.country, "Source family": source.source_family.value, "Source type": source.source_type.value, "Source role": source.source_role.value, "Evidence label": source.evidence_label, "Name": source.name, "Discovery URL": source.url, "Organisation": source.organisation, "Category": source.category, "Max articles": source.max_articles_per_scan, "Listing pages": source.max_listing_pages} for index, source in enumerate(sources)], columns=EDITOR_COLUMNS)
    revision = st.session_state.get("source_editor_revision", 0)
    with st.form(f"source_bulk_editor_{revision}"):
        edited = st.data_editor(
            table,
            hide_index=True,
            num_rows="dynamic",
            key=f"source_editor_{revision}",
            disabled=["_key"],
            width="stretch",
            column_order=["Enabled", "Browser", "Country", "Source family", "Source type", "Source role", "Evidence label", "Name", "Discovery URL", "Organisation", "Category", "Max articles", "Listing pages"],
            column_config={
                "_key": None,
                "Enabled": st.column_config.CheckboxColumn(default=True),
                "Browser": st.column_config.CheckboxColumn("Browser"),
                "Country": st.column_config.TextColumn(default="Unknown"),
                "Source family": st.column_config.SelectboxColumn("Source family", options=[item.value for item in SourceFamily]),
                "Source type": st.column_config.SelectboxColumn("Source type", options=[item.value for item in SourceType]),
                "Source role": st.column_config.SelectboxColumn("Source role", options=[item.value for item in SourceRole]),
                "Evidence label": st.column_config.SelectboxColumn("Evidence label", options=["standards / guidance", "official guidance / research", "news / commentary", "catalogue / training", "press release / official notice", "research / report"]),
                "Name": st.column_config.TextColumn(required=True),
                "Discovery URL": st.column_config.TextColumn(required=True),
                "Organisation": st.column_config.TextColumn(required=True),
                "Category": st.column_config.TextColumn(default="Uncategorised"),
                "Max articles": st.column_config.NumberColumn(min_value=1, max_value=100, default=25),
                "Listing pages": st.column_config.NumberColumn(min_value=1, max_value=25, default=5),
            },
        )
        validate = st.form_submit_button("Validate catalogue changes", type="primary")
    if validate:
        st.session_state.pop("pending_source_catalogue", None)
        try:
            proposed = _sources_from_table(sources, edited)
            services["source_configuration_workflow"].validate_catalogue(proposed)
            st.session_state["pending_source_catalogue"] = proposed
            st.session_state["pending_source_baseline"] = list(sources)
            st.success("Catalogue is valid. Review the proposed changes below before applying them.")
        except ConfigurationError as error:
            st.error(str(error))
    pending = st.session_state.get("pending_source_catalogue")
    if pending is not None:
        _render_pending_changes(services, sources, pending)


def _render_pending_changes(services: dict, current: list[Source], pending: list[Source]) -> None:
    if st.session_state.get("pending_source_baseline") != current:
        st.session_state.pop("pending_source_catalogue", None)
        st.info("The source catalogue changed after this draft was validated. Please validate the edit table again before applying changes.")
        return
    changes = _describe_changes(current, pending)
    if not changes:
        st.info("The draft contains no changes.")
        st.session_state.pop("pending_source_catalogue", None)
        return
    st.warning(f"{len(changes)} proposed change(s). Review before applying.")
    st.dataframe(pd.DataFrame(changes), hide_index=True, width="stretch")
    newly_enabled = [item["Source"] for item in changes if item["Change"] == "Enabled source"]
    if newly_enabled:
        st.warning("Sources being enabled: " + ", ".join(newly_enabled))
    removed = [row for row in changes if row["Change"] == "Removed source"]
    confirmed = not removed or st.checkbox(f"I understand that {len(removed)} source(s) will be removed from the active catalogue; past evidence is kept.")
    first, second = st.columns(2)
    if first.button("Apply validated changes", type="primary", disabled=not confirmed):
        try:
            services["source_configuration_workflow"].replace_catalogue(pending)
            st.session_state.pop("pending_source_catalogue", None)
            st.session_state["source_editor_revision"] = st.session_state.get("source_editor_revision", 0) + 1
            st.success("Source catalogue updated.")
            st.rerun()
        except ConfigurationError as error:
            st.error(str(error))
    if second.button("Discard draft"):
        st.session_state["source_editor_revision"] = st.session_state.get("source_editor_revision", 0) + 1
        st.session_state.pop("pending_source_catalogue", None)
        st.rerun()


def _render_grouped_enabled_sources(services: dict, sources: list[Source]) -> None:
    st.subheader("Enabled sources by type and organisation")
    health = services["scan_repository"].list_source_health()
    grouped: dict[str, dict[str, list[Source]]] = {}
    for source in sources:
        grouped.setdefault(source.source_family.value, {}).setdefault(source.organisation, []).append(source)
    family_order = [item.value for item in (SourceFamily.PROFESSIONAL_BODY, SourceFamily.HIGHER_LEARNING, SourceFamily.GOVERNMENT_AGENCY)]
    for source_family in family_order:
        orgs = grouped.get(source_family, {})
        if not orgs:
            continue
        with st.expander(_family_badge(SourceFamily(source_family)), expanded=False):
            st.caption(_family_description(SourceFamily(source_family)))
            for organisation in sorted(orgs):
                st.caption(organisation)
                rows = []
                for source in sorted(orgs[organisation], key=lambda item: item.evidence_label):
                    rows.append({
                        "Name": source.name,
                        "Country": source.country,
                        "Source family": _family_badge(source.source_family),
                        "Source type": _type_badge(source.source_type),
                        "Source role": source.source_role.value,
                        "Evidence label": source.evidence_label,
                        "Discovery URL": source.url,
                        "Category": source.category,
                        "Evidence records": health.get(source.id).evidence_count if source.id in health else 0,
                        "Last evidence": health[source.id].last_evidence_at.strftime("%Y-%m-%d %H:%M") if source.id in health else "Not yet scanned",
                        "Max articles": source.max_articles_per_scan,
                        "Listing pages": source.max_listing_pages,
                    })
                st.dataframe(rows, hide_index=True, width="stretch")
EDITOR_COLUMNS = ["_key", "Enabled", "Browser", "Country", "Source family", "Source type",
                  "Source role", "Evidence label", "Name", "Discovery URL", "Organisation",
                  "Category", "Max articles", "Listing pages"]


def _row_key(source, index):
    return f"id:{source.id}" if source.id is not None else f"row:{index}"


def _sources_from_table(current: list[Source], table: pd.DataFrame) -> list[Source]:
    """Map rows by immutable hidden keys, never position or editable URLs."""
    lookup = {_row_key(source, i): source for i, source in enumerate(current)}
    proposed, seen = [], set()
    for number, (_, row) in enumerate(table.iterrows(), 1):
        def value(name, default):
            result = row.get(name)
            return default if result is None or pd.isna(result) or result == "" else result
        key = value("_key", None)
        if key is not None and (key not in lookup or key in seen):
            raise ConfigurationError(f"Row {number}: stale or duplicate source identity. Reload the editor.")
        seen.add(key)
        old = lookup[key] if key else Source(None, "", "", "", country="Unknown", llm_allowed=False)
        try:
            for name in ("Name", "Discovery URL", "Organisation"):
                if not str(value(name, "")).strip():
                    raise ValueError(f"{name} is required")
            def integer(name, default):
                raw = float(value(name, default))
                if not raw.is_integer():
                    raise ValueError(f"{name} must be a whole number")
                return int(raw)
            proposed.append(replace(old,
                name=str(value("Name", "")).strip(), url=str(value("Discovery URL", "")).strip(),
                organisation=str(value("Organisation", "")).strip(),
                country=str(value("Country", old.country or "Unknown")),
                enabled=bool(value("Enabled", old.enabled)),
                use_browser_rendering=bool(value("Browser", old.use_browser_rendering)),
                category=str(value("Category", old.category)),
                source_family=SourceFamily(value("Source family", old.source_family.value)),
                source_type=SourceType(value("Source type", old.source_type.value)),
                source_role=SourceRole(value("Source role", old.source_role.value)),
                evidence_label=str(value("Evidence label", old.evidence_label)),
                max_articles_per_scan=integer("Max articles", 25),
                max_listing_pages=integer("Listing pages", 5)))
        except (ValueError, TypeError, OverflowError) as error:
            raise ConfigurationError(f"Row {number}: {error}") from error
    return proposed


def _describe_changes(current: list[Source], pending: list[Source]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    old_by_key = {(s.id if s.id is not None else s.url): s for s in current}
    retained = set()
    for new in pending:
        key = new.id if new.id is not None else new.url
        old = old_by_key.get(key)
        if old is None:
            changes.append({"Source": new.name, "Change": "Added source", "From": "", "To": new.url})
            continue
        retained.add(key)
        for label, old_value, new_value in (("Name", old.name, new.name), ("Discovery URL", old.url, new.url), ("Organisation", old.organisation, new.organisation), ("Country", old.country, new.country), ("Source family", _family_badge(old.source_family), _family_badge(new.source_family)), ("Source type", _type_badge(old.source_type), _type_badge(new.source_type)), ("Source role", old.source_role.value, new.source_role.value), ("Category", old.category, new.category), ("Max articles", str(old.max_articles_per_scan), str(new.max_articles_per_scan)), ("Listing pages", str(old.max_listing_pages), str(new.max_listing_pages)), ("Article URL pattern", old.article_url_pattern, new.article_url_pattern), ("Enabled", str(old.enabled), str(new.enabled))):
            if old_value != new_value:
                change = "Enabled source" if label == "Enabled" and new.enabled else "Disabled source" if label == "Enabled" else f"Changed {label}"
                changes.append({"Source": new.name, "Change": change, "From": old_value, "To": new_value})
        if old.evidence_label != new.evidence_label:
            changes.append({"Source": new.name, "Change": "Changed Evidence label", "From": old.evidence_label, "To": new.evidence_label})
        if old.use_browser_rendering != new.use_browser_rendering:
            changes.append({"Source": new.name, "Change": "Changed Browser", "From": str(old.use_browser_rendering), "To": str(new.use_browser_rendering)})
    for key, old in old_by_key.items():
        if key not in retained:
            changes.append({"Source": old.name, "Change": "Removed source", "From": old.url, "To": ""})
    return changes


def _catalogue_shape_changed(current: list[Source], pending: list[Source]) -> bool:
    """Return whether a pending edit draft no longer matches the live catalogue."""
    return [source.url for source in current] != [source.url for source in pending]


def _catalogue_preview_changes(current: list[Source], preview: list[Source]) -> list[dict[str, str]]:
    """Summarise URL-level differences in an uploaded catalogue backup."""
    current_by_url = {source.url: source for source in current}
    preview_by_url = {source.url: source for source in preview}
    changes: list[dict[str, str]] = []
    for url in sorted(preview_by_url.keys() - current_by_url.keys()):
        changes.append({"Change": "Would add", "Source": preview_by_url[url].name, "URL": url})
    for url in sorted(current_by_url.keys() - preview_by_url.keys()):
        changes.append({"Change": "Would remove", "Source": current_by_url[url].name, "URL": url})
    for url in sorted(current_by_url.keys() & preview_by_url.keys()):
        current_source = current_by_url[url]
        preview_source = preview_by_url[url]
        if _source_signature(current_source) != _source_signature(preview_source):
            changes.append({"Change": "Would update", "Source": preview_source.name, "URL": url})
    return changes


def _source_signature(source: Source) -> tuple:
    """Return comparable source fields excluding database identity."""
    return (
        source.name,
        source.url,
        source.organisation,
        source.country,
        source.enabled,
        source.category,
        source.max_articles_per_scan,
        source.article_url_pattern,
        source.is_active,
        source.max_listing_pages,
        source.use_browser_rendering,
        source.evidence_label,
        source.source_type,
        source.source_role,
        source.llm_allowed,
        source.source_family,
    )
