# 数据模型：一条待办长什么样，以及它和 dict 之间怎么互转。

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    # 注意：不能写 created_at: str = datetime.now().isoformat()，那样所有对象共用一个时间
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    # 同理，不能写 tags: list[str] = []，dataclass 会直接报错
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转成能塞进 JSON 的 dict。"""
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "created_at": self.created_at,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Todo":
        """从 JSON 读出来的 dict 还原成 Todo。"""
        return cls(
            id=data["id"],
            title=data["title"],
            done=data.get("done", False),
            created_at=data.get("created_at") or datetime.now().isoformat(timespec="seconds"),
            tags=list(data.get("tags") or []),
        )
