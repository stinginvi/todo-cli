# 数据层：所有读写都走这里，命令行层不直接碰文件。

import json
from pathlib import Path

from models import Todo


class TodoStore:
    def __init__(self, path: str | Path = "todos.json"):
        self.path = Path(path)
        self.todos: list[Todo] = []
        self._max_id = 0          # 记住见过的最大 id，删除后也不回退
        self._load()

    # ---------- 内部：和文件打交道 ----------
    def _load(self) -> None:
        """文件不存在 → 空列表；文件损坏 → 抛 ValueError("待办文件损坏：...")。"""
        if not self.path.exists():
            self.todos = []
            self._max_id = 0
            return

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"待办文件损坏：{e}") from e

        if not isinstance(data, list):
            raise ValueError("待办文件损坏：最外层应是列表")

        try:
            self.todos = [Todo.from_dict(item) for item in data]
        except (KeyError, TypeError, AttributeError) as e:
            raise ValueError(f"待办文件损坏：{e}") from e

        self._max_id = max((t.id for t in self.todos), default=0)

    def _save(self) -> None:
        """把 self.todos 写回文件，indent=2、ensure_ascii=False。"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps([t.to_dict() for t in self.todos], indent=2, ensure_ascii=False)
        self.path.write_text(text + "\n", encoding="utf-8")

    # ---------- 对外：增删改查 ----------
    def add(self, title: str, tags: list[str] | None = None) -> Todo:
        """新增一条，返回新增的 Todo。每次修改后立刻存盘。"""
        self._max_id += 1
        todo = Todo(
            id=self._max_id,
            title=title,
            tags=list(tags) if tags is not None else [],
        )
        self.todos.append(todo)
        self._save()
        return todo

    def list(self, done: bool | None = None, tag: str | None = None) -> list[Todo]:
        """列出待办。done=True 只看已完成，False 只看未完成，None 全部。"""
        result: list[Todo] = []
        for todo in self.todos:
            if done is not None and todo.done != done:
                continue
            if tag is not None and tag not in todo.tags:
                continue
            result.append(todo)
        return result

    def mark_done(self, todo_id: int) -> bool:
        """标记完成，找不到返回 False。"""
        for todo in self.todos:
            if todo.id == todo_id:
                todo.done = True
                self._save()
                return True
        return False

    def remove(self, todo_id: int) -> bool:
        """删除，找不到返回 False。"""
        for index, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[index]
                self._save()
                return True
        return False
