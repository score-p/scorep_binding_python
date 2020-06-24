import os
import scorep.helper


def test_add_to_ld_library_path(monkeypatch):
    # Previous value: Empty
    monkeypatch.setenv('LD_LIBRARY_PATH', '')
    scorep.helper.add_to_ld_library_path('/my/path')
    assert os.environ['LD_LIBRARY_PATH'] == '/my/path'
    # Don't add duplicates
    scorep.helper.add_to_ld_library_path('/my/path')
    assert os.environ['LD_LIBRARY_PATH'] == '/my/path'
    # Prepend
    scorep.helper.add_to_ld_library_path('/new/folder')
    assert os.environ['LD_LIBRARY_PATH'] == '/new/folder:/my/path'
    # also no duplicates:
    for p in ('/my/path', '/new/folder'):
        scorep.helper.add_to_ld_library_path(p)
        assert os.environ['LD_LIBRARY_PATH'] == '/new/folder:/my/path'

    # Add parent folder of existing one
    monkeypatch.setenv('LD_LIBRARY_PATH', '/some/folder:/parent/sub')
    scorep.helper.add_to_ld_library_path('/parent')
    assert os.environ['LD_LIBRARY_PATH'] == '/parent:/some/folder:/parent/sub'
