"""
答案生成器 - 从知识库生成答案
"""

from typing import Dict, List


class AnswerGenerator:
    """答案生成器"""

    def __init__(self, fact_kb):
        self.fact_kb = fact_kb

    def generate(self, question_type: str, entity: str, full_question: str = "", relation: str = "") -> str:
        """生成答案"""
        if question_type == "WHO_IS":
            return self._generate_who_is(entity)
        elif question_type == "WHO_IS_REVERSE":
            return self._generate_reverse_relation(entity, relation)
        elif question_type == "RELATION":
            return self._generate_relation(entity, full_question)
        elif question_type == "WHAT_DID":
            return self._generate_what_did(entity)
        else:
            return self._generate_generic(entity)

    def _generate_who_is(self, entity: str) -> str:
        """X是谁"""
        rels = self.fact_kb.get_relations_by_subject(entity)
        if rels:
            parts = []
            for rel, obj in rels:
                if rel == "是":
                    parts.append(f"是{obj}")
                elif rel == "像":
                    parts.append(f"像{obj}")
                else:
                    parts.append(f"{rel}是{obj}")
            return f"{entity}，" + "，".join(parts)

        info = self.fact_kb.get_entity(entity)
        if info:
            return f"{entity}是一个{info.get('type', '未知')}。"

        return f"抱歉，我在知识库中没有找到关于'{entity}'的信息。"

    def _generate_reverse_relation(self, entity: str, relation: str) -> str:
        """X的Y是谁 → 查反向关系

        例：猪八戒的师兄是谁？→ relation=师兄, entity=猪八戒
        例：唐僧带着谁去取经？→ relation=取经, entity=唐僧
        """
        # 特殊处理：关系是"取经"时，查询"带着"
        if relation == "取经":
            # 查(entity, 带着, *) 获取被带的人
            results = []
            for (subj, rel), objs in self.fact_kb.relations.items():
                if subj == entity and rel == "带着":
                    results.extend(objs)
            if results:
                return f"{entity}带着{'、'.join(results)}去取经"
            return f"抱歉，我没有找到{entity}带着谁的信息。"

        # 正常反向关系查询
        results = []
        for (subj, rel), objs in self.fact_kb.relations.items():
            if rel == relation and entity in objs:
                results.append(subj)

        if results:
            return f"{entity}的{relation}是{'、'.join(results)}"

        direct = self.fact_kb.get_relation(entity, relation)
        if direct:
            return f"{entity}的{relation}是{direct}"

        return f"抱歉，我没有找到'{entity}的{relation}'的信息。"

    def _generate_relation(self, entity: str, full_question: str) -> str:
        """X和Y的关系"""
        parts = entity.split("和")
        if len(parts) == 2:
            x, y = parts[0].strip(), parts[1].strip()
            for (subj, rel), obj in self.fact_kb.relations.items():
                if subj == x and obj == y:
                    return f"{x}是{y}的{rel}"
                if subj == y and obj == x:
                    return f"{y}是{x}的{rel}"
        return f"抱歉，我没有找到相关关系信息。"

    def _generate_what_did(self, entity: str) -> str:
        """X做了什么"""
        events = self.fact_kb.get_events_by_subject(entity)
        if events:
            parts = []
            for e in events:
                result = e.get("result", "")
                name = e.get("name", "")
                if name and result:
                    parts.append(f"{name}：{result}")
            return "；".join(parts) if parts else f"关于{entity}，没有找到事件记录。"
        return f"关于{entity}，没有找到事件记录。"

    def _generate_generic(self, entity: str) -> str:
        """通用查询"""
        info = self.fact_kb.get_entity(entity)
        if info:
            return f"{entity}是一个{info.get('type', '未知')}。"

        rels = self.fact_kb.get_relations_by_subject(entity)
        if rels:
            parts = [f"{rel}是{obj}" for rel, obj in rels]
            return f"{entity}，" + "，".join(parts)

        return f"抱歉，我在知识库中没有找到关于'{entity}'的详细信息。"


def demo():
    from kb.fact_kb import FactKB

    kb = FactKB()
    kb.add_relation({"subject": "孙悟空", "relation": "师兄", "object": "猪八戒"})
    kb.add_relation({"subject": "猪八戒", "relation": "师弟", "object": "孙悟空"})
    kb.add_relation({"subject": "孙悟空", "relation": "师父", "object": "唐僧"})
    kb.add_relation({"subject": "唐僧", "relation": "带着", "object": "孙悟空"})
    kb.add_relation({"subject": "唐僧", "relation": "带着", "object": "猪八戒"})
    kb.add_relation({"subject": "唐僧", "relation": "带着", "object": "沙僧"})

    gen = AnswerGenerator(kb)

    print("【答案生成测试】")
    print(f"  孙悟空是谁: {gen.generate('WHO_IS', '孙悟空')}")
    print(f"  猪八戒的师兄是谁: {gen.generate('WHO_IS_REVERSE', '猪八戒', '', '师兄')}")
    print(f"  唐僧带着谁去取经: {gen.generate('WHO_IS_REVERSE', '唐僧', '', '去取经')}")


if __name__ == "__main__":
    demo()