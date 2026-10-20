import json
from pathlib import Path
from src.services.configuration_service import ConfigurationService
from src.services.master_scan_plan import compile_plan
from src.services.session_workspace import build_session_services
from src.scanner.competency_pilot import PilotCollector, make_card, serial
from src.services.competency_export import build_competency_handover


def test_master_has_all_parents_and_enabled_safe_sources():
    root = Path(__file__).resolve().parents[1]
    sources = ConfigurationService(root / 'config/sources.yaml').load_sources()
    plan = json.loads((root / 'config/competency_scan_plan.json').read_text())
    assert len(sources) == len(plan) == 164
    assert len({s.organisation for s in sources}) == 106
    assert all(s.enabled and not s.llm_allowed for s in sources)
    assert all(p['mode'] == 'DISCOVER' for p in plan if p['requested_mode'] == 'DROP_OR_DISCOVER')
    assert {s.url for s in sources if s.organisation == 'Ngee Ann Polytechnic'} == {
        'https://www.moe.gov.sg/coursefinder/coursedetail/n50-mechatronics-and-robotics',
        'https://www.moe.gov.sg/coursefinder/coursedetail/n44-electronic-and-computer-engineering'}


def test_unknown_parent_cannot_get_invented_url():
    import pytest
    with pytest.raises(ValueError, match='No recorded URL'):
        compile_plan([dict(Parent_organisation='Missing', Scan_mode='SCAN')], [], [], [])


def test_session_workflow_isolates_source_errors_and_exports_real_logs(tmp_path):
    from src.workflow.competency_scan_workflow import CompetencyScanWorkflow
    (tmp_path / 'config').mkdir()
    source = dict(name='Example', organisation='Example', url='https://example.org/course', enabled=True, source_type='CATALOGUE')
    (tmp_path / 'config/sources.yaml').write_text(json.dumps({'sources':[source,dict(source,name='Failure',url='https://example.org/fail')]}))
    services = build_session_services(tmp_path)
    class FakeCollector(PilotCollector):
        def run(self, rows):
            row = rows[0]
            if row['URL'].endswith('fail'):
                raise ValueError('Synthetic fetch failure')
            card = make_card(row,row['URL'],'Engineering curriculum',['Engineering curriculum includes control systems, robotics, simulation and technical design requirements.'],5000)
            self.cards.append(card)
            self.log(row,row['URL'],200,attempted=True).update(cards_produced=1,chars=len(serial(card)))
    workflow = CompetencyScanWorkflow(services['source_repository'],services['scan_repository'],[],FakeCollector)
    progress = []
    run = workflow.run(progress_callback=lambda *args:progress.append(args))
    assert run.completed_at and len(workflow.result['cards']) == 1
    assert progress[-1][0] == 2
    files = build_competency_handover(run,services['scan_repository'].list_evidence_for_run(run.id),scan_summary={'competency_result':workflow.result})
    assert json.loads(files['cards_part_001.txt']) == workflow.result['cards']
    assert b'200' in files['url_log.txt'] and b'ROW_FAILED' in files['url_log.txt']
    assert len(serial(workflow.result['cards'][0])) <= 1000
    services['connection'].close()
