"""Current framework viewing and officer-controlled import page."""
from collections import Counter
import streamlit as st
from src.core.exceptions import FrameworkImportError


def _fmt(dt_value) -> str:
    return dt_value.strftime("%Y-%m-%d %H:%M") if dt_value else "Unknown"


def render(services: dict) -> None:
    """Render the current framework and a validated CSV import form."""
    st.header("Current Framework")
    repository = services["framework_repository"]
    current = repository.get_current()
    if current is None:
        st.info("No framework version has been imported yet.")
    else:
        st.subheader(f"Version {current.version}")
        st.caption(f"Imported {_fmt(current.created_at)}")
        areas = repository.list_areas(current.id or 0)
        competencies = {area.id: repository.list_competencies(area.id or 0) for area in areas if area.id is not None}
        summary_left, summary_middle, summary_right = st.columns(3)
        summary_left.metric("Cap Areas", len({area.cap_area or "Unspecified" for area in areas}))
        summary_middle.metric("Sub-functional areas", len(areas))
        summary_right.metric("Competencies", sum(len(items) for items in competencies.values()))
        cap_area_counts = Counter(area.cap_area or "Unspecified" for area in areas)
        st.caption("Cap Area distribution")
        st.dataframe(
            [{"Cap Area": cap_area, "Sub-functional areas": count} for cap_area, count in cap_area_counts.most_common()],
            hide_index=True,
            width="stretch",
        )
        grouped: dict[str, list] = {}
        for area in areas:
            grouped.setdefault(area.cap_area or "Unspecified", []).append(area)
        for cap_area in sorted(grouped):
            with st.expander(f"Cap Area: {cap_area}", expanded=False):
                for area in grouped[cap_area]:
                    with st.expander(area.name):
                        if area.description:
                            st.write(area.description)
                        for competency in competencies.get(area.id, []):
                            st.markdown(f"**{competency.name}**")
                            st.caption("Definition")
                            st.write(competency.description)
    st.divider()
    st.subheader("Import a new version")
    st.caption("Import is append-only. A successful import makes the new version current; existing versions remain unchanged.")
    with st.form("framework_import"):
        version = st.text_input("Version", placeholder="e.g. 2026.1")
        uploaded = st.file_uploader("Framework file (CSV UTF-8 or XLSX)", type=["csv", "xlsx"])
        if uploaded is not None:
            try:
                columns = services["framework_service"].preview_columns(uploaded.name, uploaded.getvalue())
                st.caption("Detected columns: " + ", ".join(columns))
                if "cap_area" in [column.lower() for column in columns]:
                    st.success("Cap Area detected and will be imported into the framework structure.")
            except FrameworkImportError as error:
                st.error(str(error))
        submitted = st.form_submit_button("Validate and import", type="primary")
    if submitted:
        if uploaded is None:
            st.error("Choose a framework CSV or XLSX file.")
            return
        try:
            framework = services["framework_service"].import_file(version, uploaded.name, uploaded.getvalue())
            st.success(f"Framework version {framework.version} imported and set as current.")
            st.rerun()
        except FrameworkImportError as error:
            st.error(str(error))
