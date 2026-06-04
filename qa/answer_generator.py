"""
答案生成器 - 从知识库生成答案
"""

from typing import Dict, List, Optional


class AnswerGenerator:
    """答案生成器"""

    def __init__(self, fact_kb):
        self.fact_kb = fact_kb

    def generate(self, question_type: str, entity: str, full_question: str = "") -> str:
        """
        生成答案
        """
        # 查知识库
        answers = self.fact_kb.query(question_type, entity)

        if answers:
            return answers[0]

        # 基于实体信息生成
        entity_info = self.fact_kb.get_entity(entity)
        if entity_info:
            attrs = entity_info.get("attributes", {})
            if attrs:
                attr_parts = []
                for k, v in attrs.items():
                    attr_parts.append(f"{k}是{v}")
                return f"{entity}，{"，".join(attr_parts)}"

        # 不知道
        return f"抱歉，我在知识库中没有找到关于'{entity}'的详细信息。"

    def generate_who_is(self, entity: str) -> str:
        """X是谁"""
        # 查实体
        info = self.fact_kb.get_entity(entity)
        if info:
            attrs = info.get("attributes", {})
            if attrs:
                parts = [f"{k}是{v}" for k, v in attrs.items()]
                return f"{entity}，" + "，".join(parts)
            return f"{entity}是一个{info.get('type', '未知')}。"

        # 查关系
        answers = self.fact_kb.query("WHO_IS", entity)
        if answers:
            return answers[0]

        return f"抱歉，我在知识库中没有找到关于'{entity}'的信息。"

    def generate_relation(self, x: str, y: str) -> str:
        """X和Y的关系"""
        # 双向查关系
        rel1 = self.fact_kb.get_relation(x, "")
        rel2 = self.fact_kb.get_relation(y, "")

        results = []
        for (subj, rel), obj in self.fact_kb.relations.items():
            if subj == x and obj == y:
                results.append(f"{x}是{y}的{rel}")
            if subj == y and obj == x:
                results.append(f"{y}是{x}的{rel}")

        if results:
            return "；".join(results)
        return f"我在知识库中没有找到{x}和{y}的关系信息。"

    def generate_what_happened(self, entity: str) -> str:
        """X做了什么"""
        events = self.fact_kb.get_events_by_subject(entity)
        if events:
            parts = []
            for e in events:
                name = e.get("name", "某事件")
                result = e.get("result", "")
                parts.append(f"{name}{result}" if result else name)
            return "；".join(parts)
        return f"我没有找到关于{entity}的事件记录。"


def demo():
    from kb.fact_kb import FactKB

    kb = FactKB()
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

    gen = AnswerGenerator(kb)

    print("【答案生成演示】")
    print(f"  孙悟空中是谁: {gen.generate_who_is('孙悟空')}")
    print(f"  孙悟空和猪八戒: {gen.generate_relation('孙悟空', '猪八戒')}")


if __name__ == "__main__":
    demo()