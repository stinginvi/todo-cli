# todo-cli

一个用 Python 写的命令行待办工具，数据保存在本地 JSON 文件里，不需要数据库，没有第三方依赖。

## 功能

- 新增、列出、标记完成、删除待办
- 支持标签，可按标签筛选
- 按「已完成 / 未完成」筛选
- 数据持久化：关掉程序再打开，数据还在
- 规范的退出码，方便脚本调用

## 环境要求

- Python 3.10 及以上（用到了 `list[str]` 和 `X | None` 语法）
- 跑测试需要 `pytest`

## 快速开始

```bash
git clone https://github.com/stinginvi/todo-cli.git
cd todo-cli

python -m venv .venv
source .venv/Scripts/activate     # Windows Git Bash
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS / Linux:     source .venv/bin/activate

python main.py -h
```

## 用法

```bash
# 新增（--tag 可以重复写多个）
python main.py add "写 W2 复盘" --tag study
python main.py add "整理面试项目" --tag career --tag study

# 列出全部
python main.py list

# 按状态筛选
python main.py list --pending     # 只看未完成
python main.py list --done        # 只看已完成

# 按标签筛选
python main.py list --tag study

# 标记完成 / 删除（数字是待办的编号）
python main.py done 1
python main.py remove 3
```

### 示例输出

```text
$ python main.py list
[ ]  1  写 W2 复盘 #study
[x]  2  买牛奶 #life
[ ]  3  整理面试项目 #career

共 3 条，未完成 2 条

$ python main.py list --pending
[ ]  1  写 W2 复盘 #study
[ ]  3  整理面试项目 #career

共 2 条，未完成 2 条
```

### 指定数据文件

```bash
python main.py --file ~/data/todos.json list
```

> 注意：`--file` 是**全局参数**，必须写在子命令前面。写在 `list` 后面会被当成 `list` 的参数，报错。

## 退出码

| 退出码 | 含义 | 例子 |
|---|---|---|
| 0 | 成功（包括查询结果为空） | `todo list` 没有待办 |
| 1 | 业务错误 | `todo done 99`，编号不存在；数据文件损坏 |
| 2 | 参数用法错误 | `todo done abc`，id 不是数字 |

脚本里可以这样用：

```bash
python main.py done 1 && echo "完成" || echo "编号不存在"
```

## 数据文件

默认读写在当前目录的 `todos.json`，格式是一个数组：

```json
[
  {
    "id": 1,
    "title": "写 W2 复盘",
    "done": false,
    "created_at": "2026-11-05T21:30:12",
    "tags": ["study"]
  }
]
```

- 每次修改后立刻写回文件（write-through），进程意外退出也不丢数据
- 编号自增，**删除后不复用**
- 文件不存在时当作空列表；文件内容损坏时给出明确错误，**不会静默清空**

## 测试

```bash
python -m pytest -q
```

覆盖：数据层的增删改查、过滤、持久化、损坏文件；命令行层的输出与退出码。共 18 个测试。

## 项目结构

```
todo-cli/
├── main.py              # 命令行层：参数解析、输出、退出码
├── store.py             # 数据层：TodoStore，所有文件读写都在这
├── models.py            # 数据模型：Todo 数据类与 dict 互转
├── tests/
│   ├── test_store.py    # 数据层测试
│   └── test_cli.py      # 命令行层测试
├── pyproject.toml
└── README.md
```

分层原则：**命令行层不直接碰文件**，一切读写都经过 `TodoStore`。想换存储方式（比如换 SQLite），只改 `store.py`。

## 已知限制

- 多个进程同时写同一个文件没有加锁，可能互相覆盖
- 不支持截止日期、优先级、编辑标题
- 列表按创建顺序输出，不支持排序

## 许可

MIT
