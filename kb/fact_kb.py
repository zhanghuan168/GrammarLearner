"""
事实知识库 - 动态扩充的知识库
支持实体、关系、事件的增删改查
"""

from typing import Dict, List, Any, Optional, Tuple
import json


class FactKB:
    """事实知识库"""

    def __init__(self):
        # 实体库: {实体名: {type, attribute, ...}}
        self.entities: Dict[str, Dict] = {}
        # 关系库: {(实体1, 关系): 实体2} 或 {(实体1, 关系, 实体2): True}
        self.relations: Dict[Tuple, Any] = {}
        # 事件库: {事件名: {主角, 对象, 结果, ...}}
        self.events: Dict[str, Dict] = {}
        # 文本片段索引（用于回溯原文）
        self.texts: List[Dict] = []

    def add_entity(self, entity: Dict):
        """添加实体"""
        name = entity.get("name")
        if not name:
            return
        self.entities[name] = {
            "name": name,
            "type": entity.get("type", "未知"),
            "attributes": entity.get("attributes", {}),
            "source": entity.get("source", ""),  # 来自哪段文本
            "mentions": entity.get("mentions", [name])  # 别名/提及形式
        }

    def add_relation(self, relation: Dict):
        """添加关系 (主体, 关系类型, 客体)"""
        subj = relation.get("subject")
        rel = relation.get("relation")
        obj = relation.get("object")
        if not all([subj, rel, obj]):
            return
        key = (subj, rel)
        self.relations[key] = obj

    def add_event(self, event: Dict):
        """添加事件"""
        name = event.get("name")
        if not name:
            return
        self.events[name] = {
            "name": name,
            "subject": event.get("subject", ""),
            "object": event.get("object", ""),
            "result": event.get("result", ""),
            "source": event.get("source", "")
        }

    def add_text(self, text: str, facts: Dict):
        """添加文本及其抽取的事实"""
        self.texts.append({
            "text": text,
            "entities": facts.get("entities", []),
            "relations": facts.get("relations", []),
            "events": facts.get("events", [])
        })

    def get_entity(self, name: str) -> Optional[Dict]:
        """获取实体信息"""
        # 精确匹配
        if name in self.entities:
            return self.entities[name]
        # 别名匹配
        for entity in self.entities.values():
            if name in entity.get("mentions", []):
                return entity
        return None

    def get_relation(self, subject: str, relation: str) -> Optional[str]:
        """获取关系"""
        return self.relations.get((subject, relation))

    def get_events_by_subject(self, subject: str) -> List[Dict]:
        """获取某主体的事件"""
        return [e for e in self.events.values() if subject in e.get("subject", "")]

    def query(self, question_type: str, entity_name: str) -> List[str]:
        """
        问答查询
        question_type: WHO, WHAT, WHO_IS_X, WHAT_DID_X_DO, RELATION, ...
        """
        results = []

        if question_type == "WHO":
            # 谁是谁
            # entity_name 格式: "X是谁" 或 "X"
            target = entity_name.replace("是谁", "").replace("什么人是", "")
            # 查找关系 (X, 身份) 或 (X, 是)
            for (subj, rel), obj in self.relations.items():
                if obj == target or subj == target:
                    if rel in {"是", "身份", "角色"}:
                        results.append(f"{subj}是{obj}")
                    else:
                        results.append(f"{subj}的{rel}是{obj}")

        elif question_type == "WHO_IS":
            # X是谁
            target = entity_name.replace("是谁", "").strip()
            entity = self.get_entity(target)
            if entity:
                attrs = entity.get("attributes", {})
                if attrs:
                    attr_str = "，".join([f"{k}是{v}" for k, v in attrs.items()])
                    results.append(f"{target}是{entity.get('type', '未知')}，{attr_str}")
                else:
                    results.append(f"{target}是{entity.get('type', '未知')}")
            # 查关系
            rel = self.get_relation(target, "是")
            if rel:
                results.append(f"{target}是{rel}")

        elif question_type == "RELATION":
            # X和Y的关系
            parts = entity_name.split("和")
            if len(parts) == 2:
                x, y = parts[0].strip(), parts[1].strip()
                # x是y的...
                for (subj, rel), obj in self.relations.items():
                    if subj == x and obj == y:
                        results.append(f"{x}是{y}的{rel}")
                    if subj == y and obj == x:
                        results.append(f"{y}是{x}的{rel}")

        elif question_type == "WHAT":
            # X做了什么
            events = self.get_events_by_subject(entity_name)
            for e in events:
                result = e.get("result", "")
                if result:
                    results.append(f"{e.get('subject', entity_name)}{result}")
                else:
                    results.append(f"{e.get('subject', entity_name)}发生了{e.get('name', '')}")

        return results if results else [f"知识库中暂无关于'{entity_name}'的详细信息"]

    def save(self, path: str = "fact_kb.json"):
        """保存知识库"""
        data = {
            "entities": self.entities,
            "relations": {f"{k[0]}|{k[1]}": v for k, v in self.relations.items()},
            "events": self.events,
            "texts_count": len(self.texts)
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"知识库已保存到 {path}，含 {len(self.entities)} 实体，{len(self.relations)} 关系，{len(self.events)} 事件")

    def load(self, path: str = "fact_kb.json"):
        """加载知识库"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.entities = data.get("entities", {})
            self.relations = {
                tuple(k.split("|")): v for k, v in data.get("relations", {}).items()
            }
            self.events = data.get("events", {})
            print(f"知识库已加载，含 {len(self.entities)} 实体，{len(self.relations)} 关系")
        except FileNotFoundError:
            print("知识库文件不存在，将创建新知识库")


def demo():
    kb = FactKB()

    # 添加示例实体
    kb.add_entity({
        "name": "孙悟空",
        "type": "人物",
        "attributes": {
            "师父": "唐僧",
            "武器": "金箍棒",
            "技能": "七十二变,筋斗云",
            "身份": "唐僧徒弟"
        }
    })
    kb.add_entity({
        "name": "唐僧",
        "type": "人物",
        "attributes": {
            "徒弟": "孙悟空,猪八戒,沙僧",
            "目的地": "西天取经"
        }
    })

    # 添加关系
    kb.add_relation({"subject": "孙悟空", "relation": "师兄", "object": "猪八戒"})
    kb.add_relation({"subject": "猪八戒", "relation": "师弟", "object": "孙悟空"})
    kb.add_relation({"subject": "孙悟空", "relation": "师父", "object": "唐僧"})

    # 测试查询
    print("\n【问答测试】")
    tests = [
        ("WHO_IS", "孙悟空是谁"),
        ("WHO_IS", "唐僧是谁"),
        ("WHAT", "孙悟空"),
        ("RELATION", "孙悟空和猪八戒")
    ]

    for qtype, q in tests:
        answers = kb.query(qtype, q.replace("孙悟空是谁", "孙悟空").replace("唐僧是谁", "唐僧"))
        print(f"  问: {q}")
        print(f"  答: {answers[0] if answers else '未找到'}")
        print()


if __name__ == "__main__":
    demo()