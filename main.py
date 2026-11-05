"""todo-cli 命令行入口：解析参数 → 调 Store → 打印结果。"""

import argparse
import sys

from models import Todo
from store import TodoStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="简单的命令行待办工具")
    parser.add_argument("--file", default="todos.json", help="数据文件路径（默认 todos.json）")

    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="新增待办")
    p_add.add_argument("title", help="待办内容")
    p_add.add_argument("--tag", action="append", default=[], help="标签，可重复")

    p_list = sub.add_parser("list", help="列出待办")
    group = p_list.add_mutually_exclusive_group()
    group.add_argument("--done", action="store_true", help="只看已完成")
    group.add_argument("--pending", action="store_true", help="只看未完成")
    p_list.add_argument("--tag", help="按标签筛选")

    p_done = sub.add_parser("done", help="标记完成")
    p_done.add_argument("id", type=int)

    p_rm = sub.add_parser("remove", help="删除")
    p_rm.add_argument("id", type=int)

    return parser


def format_todo(todo: Todo) -> str:
    """一行显示一条待办，例如： [x] 1  写 W2 复盘  #study"""
    box = "x" if todo.done else " "
    tags = "".join(f" #{tag}" for tag in todo.tags)
    return f"[{box}] {todo.id:>2}  {todo.title}{tags}"


def cmd_add(store: TodoStore, args) -> int:
    todo = store.add(args.title, tags=args.tag)
    print(f"已新增 #{todo.id}：{todo.title}")
    return 0


def cmd_list(store: TodoStore, args) -> int:
    if args.done:
        done = True
    elif args.pending:
        done = False
    else:
        done = None

    todos = store.list(done=done, tag=args.tag)
    if not todos:
        print("没有符合条件的待办。")
        return 0

    for todo in todos:
        print(format_todo(todo))

    pending = sum(1 for t in todos if not t.done)
    print(f"\n共 {len(todos)} 条，未完成 {pending} 条")
    return 0


def cmd_done(store: TodoStore, args) -> int:
    if not store.mark_done(args.id):
        print(f"没有找到编号为 {args.id} 的待办。", file=sys.stderr)
        return 1
    print(f"已完成 #{args.id}")
    return 0


def cmd_remove(store: TodoStore, args) -> int:
    if not store.remove(args.id):
        print(f"没有找到编号为 {args.id} 的待办。", file=sys.stderr)
        return 1
    print(f"已删除 #{args.id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        store = TodoStore(args.file)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1

    handlers = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
        "remove": cmd_remove,
    }
    return handlers[args.command](store, args)


if __name__ == "__main__":
    sys.exit(main())
