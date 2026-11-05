# 数据层测试。跑法（在 todo-cli 目录下）：python -m pytest -q

import json

import pytest

from models import Todo
from store import TodoStore


@pytest.fixture
def store(tmp_path):
    """每个测试用一个全新的临时文件，互不干扰。"""
    return TodoStore(tmp_path / "todos.json")


def test_add(store):
    todo = store.add("写 W2 复盘", tags=["study"])
    assert todo.id == 1
    assert todo.title == "写 W2 复盘"
    assert todo.done is False
    assert todo.tags == ["study"]


def test_id_increment(store):
    a = store.add("a")
    b = store.add("b")
    assert (a.id, b.id) == (1, 2)


def test_id_not_reused_after_remove(store):
    a = store.add("a")
    store.remove(a.id)
    b = store.add("b")
    assert b.id == 2


def test_list_all(store):
    store.add("a")
    store.add("b")
    assert [t.title for t in store.list()] == ["a", "b"]


def test_list_filter_done(store):
    a = store.add("a")
    store.add("b")
    store.mark_done(a.id)
    assert [t.title for t in store.list(done=True)] == ["a"]
    assert [t.title for t in store.list(done=False)] == ["b"]


def test_list_filter_tag(store):
    store.add("a", tags=["study"])
    store.add("b", tags=["home"])
    assert [t.title for t in store.list(tag="study")] == ["a"]


def test_mark_done(store):
    a = store.add("a")
    assert store.mark_done(a.id) is True
    assert store.list()[0].done is True


def test_mark_done_missing(store):
    assert store.mark_done(99) is False


def test_remove(store):
    a = store.add("a")
    assert store.remove(a.id) is True
    assert store.list() == []


def test_remove_missing(store):
    assert store.remove(99) is False


def test_persist_between_instances(tmp_path):
    path = tmp_path / "todos.json"
    s1 = TodoStore(path)
    s1.add("记住我", tags=["x"])
    s2 = TodoStore(path)          # 新实例重新读文件
    assert [t.title for t in s2.list()] == ["记住我"]
    assert s2.list()[0].tags == ["x"]


def test_file_is_valid_json(tmp_path):
    path = tmp_path / "todos.json"
    TodoStore(path).add("a")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data[0]["title"] == "a"


def test_corrupt_file(tmp_path):
    path = tmp_path / "todos.json"
    path.write_text("{ 这不是 JSON", encoding="utf-8")
    with pytest.raises(ValueError):
        TodoStore(path)


def test_todo_roundtrip():
    todo = Todo(id=1, title="t", done=True, created_at="2026-11-04T09:00:00", tags=["a"])
    assert Todo.from_dict(todo.to_dict()) == todo
