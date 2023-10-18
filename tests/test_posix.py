import os

import pytest

from shellingham import posix
from shellingham.posix._core import Process


class EnvironManager(object):

    def __init__(self):
        self.backup = {}
        self.changed = set()

    def patch(self, **kwargs):
        self.backup.update({
            k: os.environ[k] for k in kwargs if k in os.environ
        })
        self.changed.update(kwargs.keys())
        os.environ.update(kwargs)

    def unpatch(self):
        for k in self.changed:
            try:
                v = self.backup[k]
            except KeyError:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.fixture()
def environ(request):
    """Provide environment variable override, and restore on finalize.
    """
    manager = EnvironManager()
    request.addfinalizer(manager.unpatch)
    return manager


MAPPING_EXAMPLE_KEEGANCSMITH = [
    Process(
        args=(
            "/Applications/iTerm.app/Contents/MacOS/iTerm2",
            "--server",
            "login",
            "-fp",
            "keegan",
        ),
        pid="1480",
        ppid="1477",
    ),
    Process(args=("-bash",), pid="1482", ppid="1481"),
    Process(args=("screen",), pid="1556", ppid="1482"),
    Process(args=("-/usr/local/bin/bash",), pid="1558", ppid="1557"),
    Process(
        args=(
            "/Applications/Emacs.app/Contents/MacOS/Emacs-x86_64-10_10",
            "-nw",
        ),
        pid="1706",
        ppid="1558",
    ),
    Process(
        args=("/usr/local/bin/aspell", "-a", "-m", "-B", "--encoding=utf-8"),
        pid="77061",
        ppid="1706",
    ),
    Process(args=("-/usr/local/bin/bash",), pid="1562", ppid="1557"),
    Process(args=("-/usr/local/bin/bash",), pid="87033", ppid="1557"),
    Process(args=("-/usr/local/bin/bash",), pid="84732", ppid="1557"),
    Process(args=("-/usr/local/bin/bash",), pid="89065", ppid="1557"),
    Process(args=("-/usr/local/bin/bash",), pid="80216", ppid="1557"),
]


@pytest.mark.parametrize('mapping, result', [
    (   # Based on pypa/pipenv#2496, provided by @keegancsmith.
        MAPPING_EXAMPLE_KEEGANCSMITH, ('bash', '==MOCKED=LOGIN=SHELL==/bash'),
    ),
])
def test_get_shell(mocker, environ, mapping, result):
    environ.patch(SHELL="==MOCKED=LOGIN=SHELL==/bash")
    mocker.patch.object(posix, "_iter_process_parents", return_value=mapping)
    assert posix.get_shell(pid=77061) == result
