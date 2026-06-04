"""
规则引擎 - 从句法树抽取事实
参考演绎层v8的两阶段设计：规则匹配 → 事实入库

改进：处理"的"字结构和连动句（合并单字名词）
"""

from typing import Dict, List, Tuple


class RuleEngine:
    """规则引擎：从句法分析结果中抽取事实"""

    def __init__(self):
        # 已知双字词（用于合并被拆分的名词）
        self.known_words = {
            "猪八戒", "孙悟空", "沙僧", "唐僧", "西天", "取经",
            "观音", "菩萨", "长坂坡", "诸葛亮", "隆中", "蜀国",
            "关羽", "张飞", "刘备", "孟获", "司马懿",
            "金箍棒", "九齿钉耙", "筋斗云", "火眼金睛",
            "花果山", "五行山", "流沙河"
        }

        # 事实模式规则
        self.pattern_rules = {
            "SV": self._extract_sv,
            "SVC": self._extract_svc,
            "SVO": self._extract_svo,
            "BA": self._extract_ba,
            "BEI": self._extract_bei,
            "SV_V": self._extract_sv_v,
            "NP_V_NP": self._extract_np_v_np,
        }

        # 动词→关系映射
        self.verb_relation_map = {
            "是": "是", "像": "像", "成为": "成为", "变成": "变成",
            "有": "有", "会": "会", "能": "能", "喜欢": "喜欢", "爱": "爱",
            "帮助": "帮助", "收": "收", "带": "带", "去": "去",
            "守护": "守护", "住": "住在", "收": "收",
        }

    def extract_facts(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """从句法树抽取事实"""
        tree_type = tree.get("type", "UNKNOWN")
        facts = {"entities": [], "relations": [], "events": []}
        if tree_type in self.pattern_rules:
            facts = self.pattern_rules[tree_type](tree, pos_tags)
        return facts

    # ========== 工具函数 ==========

    def _merge_noun_block(self, pos_tags: List[Tuple], start_idx: int) -> Tuple[str, int]:
        """合并相邻的名词块，返回 (合并后的词, 跳过的token数)"""
        n = len(pos_tags)
        if start_idx >= n:
            return "", 0

        current_word = pos_tags[start_idx][0]

        # 检查能否与下一个字合成双字词
        if start_idx + 1 < n:
            next_word = pos_tags[start_idx + 1][0]
            combined = current_word + next_word
            if combined in self.known_words:
                return combined, 2

        return current_word, 1

    def _get_reverse_relation(self, relation: str) -> str:
        """获取反向关系名称"""
        reverse_map = {
            "师弟": "师兄",
            "师兄": "师弟",
            "徒弟": "师父",
            "师父": "徒弟",
            "儿子": "父亲",
            "父亲": "儿子",
            "女儿": "父亲",
            "哥哥": "弟弟",
            "弟弟": "哥哥",
            "姐姐": "妹妹",
            "妹妹": "姐姐",
            "丈夫": "妻子",
            "妻子": "丈夫",
        }
        return reverse_map.get(relation, "")

    def _get_noun_tokens(self, pos_tags: List[Tuple]) -> List[str]:
        """提取所有名词token，合并连续的单字名词

        例如：[圆(N), 盘(N)] → ["圆盘"]（相邻单字合并）
             [沙(N), 僧(N)] → ["沙僧"]（已知词合并）
             [第三(NUM), 个(Q), 徒弟(N)] → ["徒弟"]（跳过数量词）
        """
        result = []
        i = 0
        n = len(pos_tags)
        while i < n:
            w, p = pos_tags[i]
            if p in {"N", "PN"}:
                merged = w
                # 尝试与下一个字合并
                if i + 1 < n and pos_tags[i + 1][1] in {"N", "PN"}:
                    next_word = pos_tags[i + 1][0]
                    combined = w + next_word
                    # 已知词优先
                    if combined in self.known_words:
                        merged = combined
                        i += 2
                        result.append(merged)
                        continue
                    # 两个相邻单字名词（非量词/数词）合并
                    excluded = {"一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
                               "个", "只", "条", "本", "次", "把", "根", "位", "名", "第", "几"}
                    if w not in excluded and next_word not in excluded:
                        merged = combined
                        i += 2
                        result.append(merged)
                        continue
                result.append(merged)
                i += 1
            elif p == "NUM" and w in {"第"}:
                # 跳过"第"这类序数标记
                i += 1
            else:
                i += 1
        return result

    # ========== 抽取函数 ==========

    def _extract_sv(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主谓句"""
        entities = []
        for word, pos in pos_tags:
            if pos in {"N", "PN"}:
                entities.append({"name": word, "type": "实体", "mentions": [word]})
        return {"entities": entities, "relations": [], "events": []}

    def _extract_svc(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主系表：处理 "X是Y的Z" 结构

        例：猪八戒是孙悟空的师弟 → (猪八戒, 师弟, 孙悟空)
        例：沙僧是唐僧的徒弟 → (沙僧, 徒弟, 唐僧)
        """
        entities = []
        relations = []

        # 找系动词位置
        copula_idx = None
        for i, (w, p) in enumerate(pos_tags):
            if p == "V_COP":
                copula_idx = i
                break

        if not copula_idx or copula_idx == 0 or copula_idx >= len(pos_tags) - 1:
            return {"entities": entities, "relations": relations, "events": []}

        # 提取主语（合并系动词前可能连续的单字名词）
        # 例如：沙+僧+是 → subject = "沙僧"
        subj_end = copula_idx - 1
        subj_start = subj_end
        # 向前合并连续的单字名词
        while subj_start > 0 and pos_tags[subj_start][1] in {"N", "PN"}:
            prev_word = pos_tags[subj_start - 1][0]
            curr_word = pos_tags[subj_start][0]
            combined = prev_word + curr_word
            if combined in self.known_words or (len(prev_word) == 1 and len(curr_word) == 1):
                subj_start -= 1
            else:
                break

        subject_tokens = pos_tags[subj_start:subj_end + 1]
        subject = "".join([w for w, p in subject_tokens])
        # 如果合并后不是已知词，再试一次从copula-1向前合并单字
        if subject not in self.known_words:
            # 简单方案：直接取copula-1的词，如果相邻可以合并的话
            w1 = pos_tags[copula_idx - 1][0]
            if subj_start > 0:
                w0 = pos_tags[subj_start - 1][0]
                if w0 + w1 in self.known_words:
                    subject = w0 + w1

        copula_word = pos_tags[copula_idx][0]
        after_copula = pos_tags[copula_idx + 1:]

        entities.append({"name": subject, "type": "人物", "mentions": [subject]})

        if copula_word == "是":
            # 查找 "的" 字
            de_idx = None
            for i, (w, p) in enumerate(after_copula):
                if w == "的":
                    de_idx = i
                    break

            if de_idx is not None and de_idx > 0:
                # X是Y的Z 结构
                y_tokens = after_copula[:de_idx]  # Y部分（关系对象）
                z_tokens = after_copula[de_idx + 1:]  # Z部分（关系名）

                # 合并Y
                y_name, _ = self._merge_noun_block(y_tokens, 0)

                # 合并Z（关系名）- 跳过"第"等修饰词，只取第一个真正的关系名词
                z_name = ""
                skip_next_num = False
                for idx, (w, p) in enumerate(z_tokens):
                    # 跳过"第"、数量词等修饰成分
                    if w == "第" or w in {"一", "二", "三", "四", "五", "六", "七", "八", "九", "十"}:
                        continue
                    if p == "NUM":
                        continue
                    if p == "Q":  # 量词
                        continue
                    if p in {"N", "ADJ"}:
                        # 合并连续名词（如"师" + "弟" → "师弟"）
                        if z_name:
                            # 已有内容，尝试合并
                            combined = z_name + w
                            if combined in self.known_words:
                                z_name = combined
                            elif len(z_name) == 1 and len(w) == 1:
                                # 相邻单字合并
                                z_name += w
                            else:
                                z_name += w
                        else:
                            z_name = w
                    else:
                        break

                # 如果z_name为空，取第一个名词
                if not z_name:
                    for w, p in z_tokens:
                        if p in {"N", "ADJ"} and w not in {"第", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"}:
                            z_name = w
                            break

                if y_name and z_name:
                    entities.append({"name": y_name, "type": "人物", "mentions": [y_name]})
                    # 正向关系：X是Y的Z → (X, Z, Y)
                    # 例：(猪八戒, 师弟, 孙悟空)
                    relations.append({
                        "subject": subject,
                        "relation": z_name,
                        "object": y_name
                    })
                    # 反向关系（自动建立）
                    reverse_rel = self._get_reverse_relation(z_name)
                    if reverse_rel and reverse_rel != z_name:
                        relations.append({
                            "subject": y_name,
                            "relation": reverse_rel,
                            "object": subject
                        })
                    return {"entities": entities, "relations": relations, "events": []}  # early exit
            else:
                # 简单判断句：X是Y
                nouns = self._get_noun_tokens(after_copula)
                if nouns:
                    complement = nouns[0]
                    if complement and complement != subject:
                        entities.append({"name": complement, "type": "描述", "mentions": [complement]})
                        relations.append({"subject": subject, "relation": "是", "object": complement})
        else:
            # 比喻句：X像Y
            nouns = self._get_noun_tokens(after_copula)
            if nouns:
                complement = nouns[0]
                if complement:
                    entities.append({"name": complement, "type": "实体", "mentions": [complement]})
                    relations.append({"subject": subject, "relation": "像", "object": complement})

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_svo(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主谓宾：查找 N-V-N 模式"""
        entities = []
        relations = []

        i = 0
        while i < len(pos_tags):
            w1, p1 = pos_tags[i]
            if p1 in {"N", "PN"} and i + 2 < len(pos_tags):
                w2, p2 = pos_tags[i + 1]
                w3, p3 = pos_tags[i + 2]
                if p2 == "V" and p3 in {"N", "PN"}:
                    verb_rel = self.verb_relation_map.get(w2, w2)
                    entities.append({"name": w1, "type": "实体", "mentions": [w1]})
                    entities.append({"name": w3, "type": "实体", "mentions": [w3]})
                    relations.append({"subject": w1, "relation": verb_rel, "object": w3})
                    i += 3
                    continue
            i += 1

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_sv_v(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """连动句：处理 "X带Y去Z" 结构

        例：唐僧带着孙悟空猪八戒沙僧去西天取经
        期望: (唐僧, 带着, 孙悟空) (唐僧, 带着, 猪八戒) (唐僧, 带着, 沙僧)
              (唐僧, 去西天取经, *)
        """
        entities = []
        relations = []

        agent = None
        patients = []
        hit_goal = False  # 标记是否遇到过"去/到"

        for i, (w, p) in enumerate(pos_tags):
            if w in {"带", "带着"} and i > 0:
                agent = pos_tags[i - 1][0]

                # 收集带之后的名词，直到遇到"去"或"到"
                j = i + 1
                while j < len(pos_tags):
                    tw, tp = pos_tags[j]
                    if tp == "PUNCT" or tw == "着":
                        j += 1
                        continue
                    if tw in {"去", "到"}:
                        hit_goal = True
                        # 遇到"去"，收集目的地信息后break
                        j += 1
                        if j < len(pos_tags):
                            next_word = pos_tags[j][0]
                            combined = next_word
                            if j + 1 < len(pos_tags) and pos_tags[j + 1][0] in self.known_words:
                                combined = next_word + pos_tags[j + 1][0]
                            if combined in self.known_words or len(next_word) == 2:
                                entities.append({"name": combined, "type": "地名", "mentions": [combined]})
                                relations.append({"subject": agent, "relation": f"去{combined}", "object": combined})
                        break
                    if tp in {"N", "PN"}:
                        patient, skip = self._merge_noun_block(pos_tags, j)
                        if patient and patient not in patients:
                            patients.append(patient)
                        j += skip
                        continue  # always continue after consuming tokens
                    j += 1

        if agent:
            entities.append({"name": agent, "type": "人物", "mentions": [agent]})
            for p in patients:
                if p != agent:
                    entities.append({"name": p, "type": "人物", "mentions": [p]})
                    relations.append({"subject": agent, "relation": "带着", "object": p})

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_np_v_np(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """兼语句"""
        entities = []
        relations = []
        return {"entities": entities, "relations": relations, "events": []}

    def _extract_ba(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """把字句"""
        entities = []
        relations = []
        for i, (w, p) in enumerate(pos_tags):
            if w == "把" and i > 0 and i + 2 < len(pos_tags):
                agent = pos_tags[i - 1][0]
                patient = pos_tags[i + 1][0]
                verb = pos_tags[i + 2][0] if i + 2 < len(pos_tags) else "未知"
                entities.append({"name": agent, "type": "人物", "mentions": [agent]})
                entities.append({"name": patient, "type": "事物", "mentions": [patient]})
                relations.append({"subject": agent, "relation": f"把{patient}{verb}", "object": verb})
        return {"entities": entities, "relations": relations, "events": []}

    def _extract_bei(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """被字句"""
        entities = []
        relations = []
        for i, (w, p) in enumerate(pos_tags):
            if w == "被" and i > 0 and i + 2 < len(pos_tags):
                patient = pos_tags[i - 1][0]
                agent = pos_tags[i + 1][0]
                verb = pos_tags[i + 2][0] if i + 2 < len(pos_tags) else "未知"
                entities.append({"name": patient, "type": "事物", "mentions": [patient]})
                entities.append({"name": agent, "type": "人物", "mentions": [agent]})
                relations.append({"subject": agent, "relation": f"把{patient}{verb}", "object": verb})
        return {"entities": entities, "relations": relations, "events": []}


def demo():
    engine = RuleEngine()

    print("【规则引擎测试】")

    # 1. SVC: X是Y的Z
    print("\n1. '猪八戒是孙悟空的师弟'")
    tags = [("猪八戒", "N"), ("是", "V_COP"), ("孙悟空", "N"), ("的", "PART"), ("师", "N"), ("弟", "N")]
    tree = {"type": "SVC"}
    facts = engine.extract_facts(tree, tags)
    print(f"  关系: {[(r['subject'], r['relation'], r['object']) for r in facts['relations']]}")

    # 2. SVC: 沙僧（单字合并）
    print("\n2. '沙僧是唐僧的徒弟'")
    tags = [("沙", "N"), ("僧", "N"), ("是", "V_COP"), ("唐", "N"), ("僧", "N"), ("的", "PART"), ("徒", "N"), ("弟", "N")]
    tree = {"type": "SVC"}
    facts = engine.extract_facts(tree, tags)
    print(f"  关系: {[(r['subject'], r['relation'], r['object']) for r in facts['relations']]}")

    # 3. SV_V: 连动句
    print("\n3. '唐僧带着孙悟空猪八戒沙僧去西天取经'")
    tags = [("唐僧", "N"), ("带", "V"), ("着", "PART"), ("孙悟空", "N"), ("猪八戒", "N"), ("沙", "N"), ("僧", "N"), ("去", "V"), ("西天", "N"), ("取经", "N")]
    tree = {"type": "SV_V"}
    facts = engine.extract_facts(tree, tags)
    print(f"  关系: {[(r['subject'], r['relation'], r['object']) for r in facts['relations']]}")

    # 4. 比喻
    print("\n4. '月亮像圆盘'")
    tags = [("月亮", "N"), ("像", "V_COP"), ("圆", "N"), ("盘", "N")]
    tree = {"type": "SVC"}
    facts = engine.extract_facts(tree, tags)
    print(f"  关系: {[(r['subject'], r['relation'], r['object']) for r in facts['relations']]}")


if __name__ == "__main__":
    demo()