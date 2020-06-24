import os
from scorep import subsystem


def test_reset_preload(monkeypatch):
    monkeypatch.setenv('LD_PRELOAD', '/some/value')
    # Nothing changes if the var is not present
    monkeypatch.delenv('SCOREP_LD_PRELOAD_BACKUP', raising=False)
    subsystem.reset_preload()
    assert os.environ['LD_PRELOAD'] == '/some/value'

    # Variable set -> Update
    monkeypatch.setenv('SCOREP_LD_PRELOAD_BACKUP', '/new/value')
    subsystem.reset_preload()
    assert os.environ['LD_PRELOAD'] == '/new/value'

    # Variable empty -> remove
    monkeypatch.setenv('SCOREP_LD_PRELOAD_BACKUP', '')
    subsystem.reset_preload()
    assert 'LD_PRELOAD' not in os.environ
