"""
规则引擎 - 从句法树抽取事实
参考演绎层v8的两阶段设计：规则匹配 → 事实入库
"""

from typing import Dict, List, Tuple


class RuleEngine:
    """规则引擎：从句法分析结果中抽取事实"""

    def __init__(self):
        # 事实模式规则
        self.pattern_rules = {
            # 主谓句模式
            "SV": self._extract_sv,
            # 主系表模式
            "SVC": self._extract_svc,
            # 主谓宾模式
            "SVO": self._extract_svo,
            # 把字句模式
            "BA": self._extract_ba,
            # 被字句模式
            "BEI": self._extract_bei,
        }

        # 常用动词→关系映射
        self.verb_relation_map = {
            "是": "是",
            "像": "像",
            "成为": "成为",
            "变成": "变成",
            "有": "有",
            "会": "会",
            "能": "能",
            "喜欢": "喜欢",
            "爱": "爱",
            "是": "身份",
        }

    def extract_facts(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """
        从句法树抽取事实
        返回: {entities: [...], relations: [...], events: [...]}
        """
        tree_type = tree.get("type", "UNKNOWN")
        facts = {"entities": [], "relations": [], "events": []}

        # 根据句法类型调用对应抽取函数
        if tree_type in self.pattern_rules:
            facts = self.pattern_rules[tree_type](tree, pos_tags)

        return facts

    def _extract_sv(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主谓句抽取：主语 + 谓语（不及物动词/形容词）"""
        entities = []
        relations = []

        for i, (word, pos) in enumerate(pos_tags):
            if pos == "N" or pos == "PN":
                entities.append({"name": word, "type": "人物/事物", "mentions": [word]})

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_svc(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主系表抽取：主语 + 是/像/成为 + 表语"""
        entities = []
        relations = []

        words = [w for w, p in pos_tags if p not in {"PART", "PUNCT"}]
        pos = [p for w, p in pos_tags if p not in {"PART", "PUNCT"}]

        # 查找系动词位置
        copula_idx = None
        for i, (w, p) in enumerate(pos_tags):
            if p == "V_COP":
                copula_idx = i
                break

        if copula_idx and copula_idx > 0 and copula_idx < len(pos_tags) - 1:
            subject = pos_tags[copula_idx - 1][0]
            complement = pos_tags[copula_idx + 1][0]

            # 添加实体
            if pos_tags[copula_idx][0] in {"是"}:
                # 判断句
                entities.append({"name": subject, "type": "实体", "mentions": [subject]})
                entities.append({"name": complement, "type": "身份/描述", "mentions": [complement]})
                relations.append({
                    "subject": subject,
                    "relation": "是",
                    "object": complement
                })
            else:
                # 比喻句
                entities.append({"name": subject, "type": "实体", "mentions": [subject]})
                relations.append({
                    "subject": subject,
                    "relation": "像",
                    "object": complement
                })

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_svo(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主谓宾抽取：主语 + 谓语(及物) + 宾语"""
        entities = []
        relations = []

        # 查找 名词-动词-名词 模式
        i = 0
        while i < len(pos_tags):
            w1, p1 = pos_tags[i]
            if p1 in {"N", "PN"} and i + 2 < len(pos_tags):
                w2, p2 = pos_tags[i + 1]
                w3, p3 = pos_tags[i + 2]
                if p2 == "V" and p3 in {"N", "PN"}:
                    # 找到 S-V-O 模式
                    entities.append({"name": w1, "type": "实体", "mentions": [w1]})
                    entities.append({"name": w3, "type": "实体", "mentions": [w3]})
                    verb_rel = self.verb_relation_map.get(w2, w2)
                    relations.append({
                        "subject": w1,
                        "relation": verb_rel,
                        "object": w3
                    })
                    i += 3
                    continue
            i += 1

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_ba(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """把字句抽取：施事把受事动作"""
        entities = []
        relations = []

        # 查找 [N]把[N][V] 模式
        for i, (w, p) in enumerate(pos_tags):
            if w == "把" and i > 0 and i + 2 < len(pos_tags):
                agent = pos_tags[i - 1][0]  # 施事
                patient = pos_tags[i + 1][0]  # 受事
                verb = pos_tags[i + 2][0]  # 动词

                entities.append({"name": agent, "type": "人物", "mentions": [agent]})
                entities.append({"name": patient, "type": "事物", "mentions": [patient]})
                relations.append({
                    "subject": agent,
                    "relation": f"把{patient}{verb}",
                    "object": verb
                })

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_bei(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """被字句抽取：受事被施事动作"""
        entities = []
        relations = []

        for i, (w, p) in enumerate(pos_tags):
            if w == "被" and i > 0 and i + 2 < len(pos_tags):
                patient = pos_tags[i - 1][0]  # 受事
                agent = pos_tags[i + 1][0]  # 施事
                verb = pos_tags[i + 2][0]  # 动词

                entities.append({"name": patient, "type": "事物", "mentions": [patient]})
                entities.append({"name": agent, "type": "人物", "mentions": [agent]})
                relations.append({
                    "subject": agent,
                    "relation": f"把{patient}{verb}",
                    "object": verb
                })

        return {"entities": entities, "relations": relations, "events": []}


def demo():
    engine = RuleEngine()

    print("【规则引擎演示】")
    # 模拟几个简单的pos_tags
    test_cases = [
        # SVO
        [("我", "PN"), ("爱", "V"), ("中国", "N")],
        # SVC
        [("小明", "N"), ("是", "V_COP"), ("学生", "N")],
        # BA
        [("我", "PN"), ("把", "P"), ("门", "N"), ("打开", "V")]
    ]

    for tags in test_cases:
        facts = engine.extract_facts({}, tags)
        print(f"  词性: {[f'{w}({p})' for w, p in tags]}")
        print(f"  事实: {facts}")
        print()


if __name__ == "__main__":
    demo()