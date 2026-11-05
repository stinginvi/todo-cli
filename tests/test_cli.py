# 命令行层测试：直接调 main(argv)，不需要真的开子进程。

import pytest

from main import main


@pytest.fixture
def data_file(tmp_path):
    return str(tmp_path / "todos.json")


def test_add_then_list(data_file, capsys):
    assert main(["--file", data_file, "add", "写复盘", "--tag", "study"]) == 0
    assert main(["--file", data_file, "list"]) == 0
    out = capsys.readouterr().out
    assert "写复盘" in out
    assert "#study" in out


def test_list_empty(data_file, capsys):
    assert main(["--file", data_file, "list"]) == 0
    assert "没有符合条件的待办" in capsys.readouterr().out


def test_done_missing_id(data_file, capsys):
    assert main(["--file", data_file, "done", "99"]) == 1
    assert "没有找到" in capsys.readouterr().err


def test_remove_then_list(data_file, capsys):
    main(["--file", data_file, "add", "买牛奶"])
    capsys.readouterr()          # 清掉 add 打印的「已新增」，只看后面 list 的输出
    assert main(["--file", data_file, "remove", "1"]) == 0
    main(["--file", data_file, "list"])
    assert "买牛奶" not in capsys.readouterr().out
