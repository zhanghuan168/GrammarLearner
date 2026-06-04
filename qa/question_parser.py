"""
问题解析器 - 将自然语言问题分类
"""

import re


class QuestionParser:
    """问题解析器"""

    def __init__(self):
        # 问题类型模式
        self.patterns = [
            # X是谁
            (r"(.+)是谁", "WHO_IS"),
            # X是谁的Y / X的Y是什么
            (r"(.+)的(.+)是什么", "WHAT_OF"),
            (r"(.+)是什么", "WHAT_IS"),
            # X做了什么 / X干什
            (r"(.+)做了(.+)", "WHAT_DID"),
            (r"(.+)干了(.+)", "WHAT_DID"),
            # X和Y的关系
            (r"(.+)和(.+)的关系", "RELATION"),
            (r"(.+)和(.+)", "RELATION"),
            # X在哪里/什么时候/怎样
            (r"(.+)在哪里", "WHERE"),
            (r"(.+)在什么时候", "WHEN"),
            (r"(.+)怎么(.+)", "HOW"),
            # 多少/多久
            (r"(.+)有多少(.+)", "HOW_MANY"),
            (r"(.+)多久(.+)", "HOW_LONG"),
        ]

    def parse(self, question: str) -> tuple:
        """
        解析问题
        返回: (问题类型, 涉及实体)
        """
        question = question.strip().replace("？", "").replace("?", "")

        for pattern, qtype in self.patterns:
            match = re.match(pattern, question)
            if match:
                entity = match.group(1).strip() if match.groups() else question
                return (qtype, entity)

        # 默认
        return ("UNKNOWN", question)


def demo():
    parser = QuestionParser()

    test_cases = [
        "孙悟空是谁？",
        "唐僧的徒弟是谁？",
        "孙悟空的师父是谁？",
        "猪八戒和孙悟空是什么关系？",
        "孙悟空会什么技能？",
        "大闹天宫是谁做的？",
        "唐僧在哪里遇到孙悟空？",
    ]

    print("【问题解析演示】")
    for q in test_cases:
        qtype, entity = parser.parse(q)
        print(f"  问: {q} → 类型: {qtype}, 实体: {entity}")


if __name__ == "__main__":
    demo()