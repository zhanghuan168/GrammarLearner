"""
事实知识库 - 动态扩充的知识库
支持实体、关系、事件的增删改查
一对多关系支持
"""

from typing import Dict, List, Any, Optional, Tuple
import json


class FactKB:
    """事实知识库"""

    def __init__(self):
        # 实体库
        self.entities: Dict[str, Dict] = {}
        # 关系库: {(主体, 关系): [客体1, 客体2, ...]}
        self.relations: Dict[Tuple[str, str], List[str]] = {}
        # 事件库
        self.events: Dict[str, Dict] = {}
        # 文本索引
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
            "source": entity.get("source", ""),
            "mentions": entity.get("mentions", [name])
        }

    def add_relation(self, relation: Dict):
        """添加关系（一对多支持）"""
        subj = relation.get("subject", "")
        rel = relation.get("relation", "")
        obj = relation.get("object", "")
        if not all([subj, rel, obj]):
            return

        key = (subj, rel)
        if key not in self.relations:
            self.relations[key] = []
        if obj not in self.relations[key]:
            self.relations[key].append(obj)

    def add_event(self, event: Dict):
        """添加事件"""
        name = event.get("name", "")
        if not name:
            return
        self.events[name] = {
            "name": name,
            "subject": event.get("subject", ""),
            "object": event.get("object", ""),
            "result": event.get("result", ""),
            "source": event.get("source", "")
        }

    def add_attribute(self, entity_name: str, attr_name: str, attr_value: str):
        """为实体添加属性（支持多值）"""
        if entity_name not in self.entities:
            self.entities[entity_name] = {
                "name": entity_name,
                "type": "未知",
                "attributes": {},
                "mentions": [entity_name]
            }
        attrs = self.entities[entity_name].setdefault("attributes", {})
        if attr_name not in attrs:
            attrs[attr_name] = []
        if isinstance(attrs[attr_name], list):
            if attr_value not in attrs[attr_name]:
                attrs[attr_name].append(attr_value)
        else:
            attrs[attr_name] = [attrs[attr_name], attr_value]

    def get_entity(self, name: str) -> Optional[Dict]:
        """获取实体"""
        if name in self.entities:
            return self.entities[name]
        for entity in self.entities.values():
            if name in entity.get("mentions", []):
                return entity
        return None

    def get_relation(self, subject: str, relation: str) -> Optional[str]:
        """获取关系（返回第一个客体）"""
        key = (subject, relation)
        objs = self.relations.get(key, [])
        return objs[0] if objs else None

    def get_relations_by_subject(self, subject: str) -> List[Tuple[str, str]]:
        """获取某主体的所有关系"""
        result = []
        for (subj, rel), objs in self.relations.items():
            if subj == subject:
                for obj in objs:
                    result.append((rel, obj))
        return result

    def get_events_by_subject(self, subject: str) -> List[Dict]:
        """获取某主体的事件"""
        return [e for e in self.events.values() if subject in e.get("subject", "")]

    def query(self, question_type: str, entity: str) -> List[str]:
        """问答查询"""
        results = []

        if question_type == "WHO_IS":
            rels = self.get_relations_by_subject(entity)
            if rels:
                parts = []
                for rel, obj in rels:
                    parts.append(f"{rel}是{obj}")
                results.append(f"{entity}，" + "，".join(parts))
            else:
                info = self.get_entity(entity)
                if info:
                    attrs = info.get("attributes", {})
                    if attrs:
                        attr_parts = []
                        for k, v in attrs.items():
                            if isinstance(v, list):
                                attr_parts.append(f"{k}是{','.join(v)}")
                            else:
                                attr_parts.append(f"{k}是{v}")
                        if attr_parts:
                            results.append(f"{entity}，" + "，".join(attr_parts))
                            return results
                    results.append(f"{entity}是一个{info.get('type', '未知')}。")
            if not results:
                results.append(f"知识库中暂无关于'{entity}'的详细信息")

        elif question_type == "WHAT":
            events = self.get_events_by_subject(entity)
            for e in events:
                result = e.get("result", "")
                name = e.get("name", "")
                if name and result:
                    results.append(f"{name}：{result}")

        elif question_type == "RELATION":
            parts = entity.split("和")
            if len(parts) == 2:
                x, y = parts[0].strip(), parts[1].strip()
                for (subj, rel), objs in self.relations.items():
                    for obj in objs:
                        if subj == x and obj == y:
                            results.append(f"{x}是{y}的{rel}")
                        if subj == y and obj == x:
                            results.append(f"{y}是{x}的{rel}")

        return results if results else [f"知识库中暂无关于'{entity}'的详细信息"]

    def save(self, path: str = "fact_kb.json"):
        """保存知识库"""
        data = {
            "entities": self.entities,
            "relations": {f"{k[0]}|{k[1]}": v for k, v in self.relations.items()},
            "events": self.events
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

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
        except FileNotFoundError:
            pass


def demo():
    kb = FactKB()
    kb.add_relation({"subject": "孙悟空", "relation": "师兄", "object": "猪八戒"})
    kb.add_relation({"subject": "猪八戒", "relation": "师弟", "object": "孙悟空"})
    kb.add_relation({"subject": "唐僧", "relation": "带着", "object": "孙悟空"})
    kb.add_relation({"subject": "唐僧", "relation": "带着", "object": "猪八戒"})
    kb.add_relation({"subject": "唐僧", "relation": "带着", "object": "沙僧"})
    kb.add_entity({"name": "及时雨", "type": "绰号"})
    kb.add_attribute("宋江", "绰号", "及时雨")

    print("【知识库测试】")
    print(f"  关系: {kb.relations}")
    print(f"  查询唐僧的关系: {kb.get_relations_by_subject('唐僧')}")


if __name__ == "__main__":
    demo()