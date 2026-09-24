"""Session-owned scan worker and thread-safe progress; no Streamlit calls."""
from threading import Lock, Thread


class ScanJob:
    def __init__(self):
        self._guard = Lock()
        self._state = dict(running=False, completed=0, total=0, source='', stage='idle', error=None)

    def snapshot(self):
        with self._guard:
            return dict(self._state)

    def start(self, services, total):
        with self._guard:
            if self._state['running']:
                return False
            self._state = dict(running=True, completed=0, total=total, source='', stage='starting', error=None)
        Thread(target=self._run, args=(services,), daemon=True).start()
        return True

    def _update(self, index, total, name, family, source_type, stage):
        with self._guard:
            self._state.update(completed=index if stage in {'done', 'error'} else max(0, index - 1),
                               total=total, source=name, stage=stage)

    def _run(self, services):
        from src.services.session_workspace import clear_current_scan
        try:
            with services['lock']:
                clear_current_scan(services)
                services['scan_workflow'].run(progress_callback=self._update)
            with self._guard:
                self._state.update(completed=self._state['total'], stage='finished')
        except Exception as error:
            with self._guard:
                self._state.update(error=f'{type(error).__name__}: {error}', stage='failed')
        finally:
            with self._guard:
                self._state['running'] = False
