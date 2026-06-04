"""
问题解析器 - 将自然语言问题分类
改进：处理"X的Y"结构，查反向关系
"""

import re


class QuestionParser:
    """问题解析器"""

    def __init__(self):
        self.patterns = [
            # X的Y是谁（如：猪八戒的师兄是谁）优先
            (r"^(.+?)的(.+?)是谁$", "WHO_IS_REVERSE"),
            # X带着谁去Y（如：唐僧带着谁去取经）
            (r"^(.+?)带着谁去(.+)$", "WHO_IS_REVERSE"),
            # X是谁（判断句）
            (r"^(.+?)是谁$", "WHO_IS"),
            # X做了什么
            (r"^(.+?)做了(.+)$", "WHAT_DID"),
            # X的Y是什么
            (r"^(.+?)的(.+?)是什么$", "WHAT_OF"),
            # X是什么
            (r"^(.+?)是什么$", "WHAT_IS"),
            # X和Y的关系
            (r"^(.+?)和(.+?)的关系$", "RELATION"),
            (r"^(.+?)和(.+)$", "RELATION"),
            # X在哪里
            (r"^(.+?)在哪里$", "WHERE"),
            (r"^(.+?)在什么时候$", "WHEN"),
            (r"^(.+?)怎么(.+)$", "HOW"),
            (r"^(.+?)有多少(.+)$", "HOW_MANY"),
            (r"^(.+?)多久(.+)$", "HOW_LONG"),
        ]

    def parse(self, question: str) -> tuple:
        """解析问题，返回 (问题类型, 涉及实体, 关系)"""
        question = question.strip().replace("？", "").replace("?", "")

        for pattern, qtype in self.patterns:
            match = re.match(pattern, question)
            if match:
                groups = match.groups()
                if qtype == "WHO_IS_REVERSE" and len(groups) >= 2:
                    # "X的Y是谁" → 实体=X，关系=Y
                    # 例如：猪八戒的师兄是谁 → entity=猪八戒, relation=师兄
                    # 查询：谁是猪八戒的师兄？→ 反向查 (谁, 师兄, 猪八戒)
                    entity = groups[0].strip()
                    relation = groups[1].strip()
                    return (qtype, entity, relation)
                else:
                    entity = groups[0].strip() if groups else question
                    return (qtype, entity, "")

        return ("UNKNOWN", question, "")


def demo():
    parser = QuestionParser()

    test_cases = [
        "孙悟空是谁？",
        "猪八戒的师兄是谁？",
        "唐僧的徒弟是谁？",
        "孙悟空的师父是谁？",
        "猪八戒和孙悟空是什么关系？",
        "孙悟空会什么技能？",
        "大闹天宫是谁做的？",
        "唐僧在哪里遇到孙悟空？",
    ]

    print("【问题解析演示】")
    for q in test_cases:
        qtype, entity, rel = parser.parse(q)
        print(f"  问: {q} → 类型:{qtype} 实体:{entity} 关系:{rel}")


if __name__ == "__main__":
    demo()