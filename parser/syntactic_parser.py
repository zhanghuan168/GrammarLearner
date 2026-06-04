"""
句法分析器 - 基于规则的句法分析
将词性序列映射到句法树
"""

from typing import Dict, List, Tuple


class SyntacticParser:
    """句法分析器"""

    def __init__(self, sentence_kb=None):
        self.sentence_kb = sentence_kb

    def parse(self, pos_tags: List[Tuple[str, str]]) -> Dict:
        """
        句法分析
        输入: [(词, 词性), ...]
        输出: 句法树
        """
        # 过滤标点
        tags = [(w, p) for w, p in pos_tags if p not in {"PUNCT", "PART"}]
        if not tags:
            return {"type": "EMPTY", "pattern": ""}

        # 检测句式类型
        sentence_type = self._detect_type(tags)

        # 构建句法树
        tree = self._build_tree(tags, sentence_type)

        return tree

    def _detect_type(self, tags: List[Tuple[str, str]]) -> str:
        """检测句式类型"""
        words = [w for w, p in tags]
        poses = [p for w, p in tags]

        # 如果有系动词（是/像/成为），优先判定为SVC
        # 因为系动词连接的是主语和表语，不是连动
        for i, (w, p) in enumerate(tags):
            if p == "V_COP":
                return "SVC"

        # 把字句
        if "把" in words:
            return "BA"

        # 被字句
        if "被" in words:
            return "BEI"

        # 连动句（两个动词连续，但排除系动词）
        v_count = sum(1 for p in poses if p == "V")
        if v_count >= 2:
            return "SV_V"

        # 兼语句（让/叫/请/派 + 人 + 动词）
        causative = {"让", "叫", "请", "派", "令", "使"}
        for i, (w, p) in enumerate(tags):
            if w in causative and i + 2 < len(tags):
                return "NP_V_NP"

        # 复句检测
        conjunctions = {"因为", "所以", "如果", "但是", "虽然", "而且", "或者", "要么", "虽然"}
        if any(w in conjunctions for w in words):
            if "因为" in words and "所以" in words:
                return "CAUSE"
            if "如果" in words or "只要" in words:
                return "COND"
            if "虽然" in words and "但是" in words:
                return "TURN"

        # 主谓宾
        if "V" in poses and "N" in poses:
            return "SVO"

        # 主谓
        return "SV"

    def _build_tree(self, tags: List[Tuple[str, str]], sentence_type: str) -> Dict:
        """构建句法树"""
        tree = {
            "type": sentence_type,
            "pattern": self._get_pattern_description(tags, sentence_type),
            "constituents": {}
        }

        if sentence_type == "SV":
            if len(tags) >= 2:
                tree["constituents"]["subject"] = tags[0][0]
                tree["constituents"]["predicate"] = tags[1][0]
            else:
                tree["constituents"]["subject"] = tags[0][0] if tags else ""

        elif sentence_type == "SVC":
            for i, (w, p) in enumerate(tags):
                if p == "V_COP":
                    tree["constituents"]["subject"] = tags[i - 1][0] if i > 0 else ""
                    tree["constituents"]["copula"] = w
                    tree["constituents"]["complement"] = tags[i + 1][0] if i + 1 < len(tags) else ""
                    break

        elif sentence_type == "SVO":
            # 查找 施事-动词-宾语 模式
            for i, (w, p) in enumerate(tags):
                if p == "V":
                    if i > 0:
                        tree["constituents"]["subject"] = tags[i - 1][0]
                    if i + 1 < len(tags):
                        tree["constituents"]["object"] = tags[i + 1][0]
                    break

        elif sentence_type == "BA":
            for i, (w, p) in enumerate(tags):
                if w == "把":
                    tree["constituents"]["agent"] = tags[i - 1][0] if i > 0 else ""
                    tree["constituents"]["patient"] = tags[i + 1][0] if i + 1 < len(tags) else ""
                    if i + 2 < len(tags):
                        tree["constituents"]["verb"] = tags[i + 2][0]
                    break

        elif sentence_type == "BEI":
            for i, (w, p) in enumerate(tags):
                if w == "被":
                    tree["constituents"]["patient"] = tags[i - 1][0] if i > 0 else ""
                    tree["constituents"]["agent"] = tags[i + 1][0] if i + 1 < len(tags) else ""
                    if i + 2 < len(tags):
                        tree["constituents"]["verb"] = tags[i + 2][0]
                    break

        elif sentence_type == "SV_V":  # 连动句
            verbs = []
            nouns = []
            for w, p in tags:
                if p == "V":
                    verbs.append(w)
                if p == "N":
                    nouns.append(w)
            tree["constituents"]["verbs"] = verbs[:2]  # 取前两个动词
            tree["constituents"]["nouns"] = nouns[:2]

        elif sentence_type == "NP_V_NP":  # 兼语句
            tree["constituents"]["predicate"] = tags[1][0] if len(tags) > 1 else ""
            tree["constituents"]["subject"] = tags[0][0] if tags else ""

        elif sentence_type == "CAUSE":
            parts = self._split_by_conjunction(tags, {"因为", "所以"})
            if len(parts) == 2:
                tree["constituents"]["cause"] = "".join([w for w, p in parts[0]])
                tree["constituents"]["effect"] = "".join([w for w, p in parts[1]])

        elif sentence_type == "COND":
            parts = self._split_by_conjunction(tags, {"如果", "就"})
            if len(parts) == 2:
                tree["constituents"]["condition"] = "".join([w for w, p in parts[0]])
                tree["constituents"]["result"] = "".join([w for w, p in parts[1]])

        return tree

    def _get_pattern_description(self, tags: List[Tuple[str, str]], sentence_type: str) -> str:
        """获取句型描述"""
        patterns = {
            "SV": "主语 + 谓语",
            "SVC": "主语 + 系动词 + 表语",
            "SVO": "主语 + 谓语 + 宾语",
            "BA": "主语 + 把 + 宾语 + 谓语",
            "BEI": "主语 + 被 + 施事 + 谓语",
            "SV_V": "主语 + 谓语1 + 谓语2（连动）",
            "NP_V_NP": "主语 + 谓语 + 兼语 + 谓语2（兼语）",
            "CAUSE": "原因 + 所以 + 结果",
            "COND": "如果 + 条件 + 就 + 结果"
        }
        return patterns.get(sentence_type, "主语 + 谓语")

    def _split_by_conjunction(self, tags, conj_set):
        """按连词分割"""
        result = []
        current = []
        for w, p in tags:
            if w in conj_set and current:
                result.append(current)
                current = []
            else:
                current.append((w, p))
        if current:
            result.append(current)
        return result


def demo():
    parser = SyntacticParser()

    test_cases = [
        # SV
        [("小猫", "N"), ("睡觉", "V")],
        # SVC
        [("小明", "N"), ("是", "V_COP"), ("学生", "N")],
        # SVO
        [("我", "PN"), ("爱", "V"), ("中国", "N")],
        # BA
        [("我", "PN"), ("把", "P"), ("门", "N"), ("打开", "V")],
        # BEI
        [("门", "N"), ("被", "P"), ("我", "PN"), ("打开", "V")],
        # CAUSE
        [("因为", "CONJ"), ("下雨", "V"), ("所以", "CONJ"), ("不去", "V")]
    ]

    print("【句法分析演示】")
    for tags in test_cases:
        tree = parser.parse(tags)
        print(f"  词性: {[f'{w}({p})' for w, p in tags]}")
        print(f"  句型: {tree['type']} - {tree['pattern']}")
        print(f"  成分: {tree['constituents']}")
        print()


if __name__ == "__main__":
    demo()