"""
规则引擎 - 从句法树抽取事实
参考演绎层v8的两阶段设计：规则匹配 → 事实入库

改进：处理"的"字结构和连动句（合并单字名词）、SVO宾语合并
"""

from typing import Dict, List, Tuple


class RuleEngine:
    """规则引擎：从句法分析结果中抽取事实"""

    def __init__(self):
        # 已知多字词（用于合并被拆分的名词）
        self.known_words = {
            "猪八戒", "孙悟空", "沙僧", "唐僧", "西天", "取经",
            "观音", "菩萨",
            "金箍棒", "九齿钉耙", "筋斗云", "火眼金睛",
            "花果山", "五行山", "流沙河",
            "刘备", "关羽", "张飞", "曹操", "孙权", "周瑜", "诸葛亮",
            "陆逊", "孙策", "华雄", "司马懿", "张辽",
            "蜀国", "江东",
            "隆中", "长坂坡",
            "宋江", "吴用", "卢俊义", "林冲", "武松", "鲁智深", "李逵", "杨志",
            "晁盖", "高俅", "方腊", "梁山泊", "及时雨", "智多星",
            "景阳冈", "生辰纲",
            "贾宝玉", "林黛玉", "薛宝钗", "王熙凤", "史湘云", "妙玉", "元春",
            "贾母", "刘姥姥", "贾府", "栊翠庵",
            "通灵宝玉", "金陵十二钗", "大观园",
            "白龙马", "唐三藏", "紧箍咒", "八卦炉",
            "天蓬元帅", "卷帘大将", "八十一难",
            # 小学常用词
            "小学生", "学生", "书包", "读书", "唱歌", "足球",
            "超市", "公园", "春游", "勇敢", "好吃", "休息", "努力",
            "下雨", "玩具", "窗户", "作业", "练习",
            "老师", "妈妈", "爸爸", "小明", "同学", "同学们",
            "新书包", "小鱼儿", "好孩子",
            "池塘", "池塘里",
            "结拜兄弟", "结拜", "清河县", "渭州",
            "表妹", "表姐", "提辖", "青龙偃月刀", "丈八蛇矛",
            "小明", "小鸟", "小鱼", "池塘里",
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
            "帮助": "帮助", "收": "收", "带": "带", "去": "去", "来": "来",
            "守护": "守护", "住在": "住在", "读": "读", "唱": "唱", "踢": "踢",
            "打": "打", "擦": "擦", "买": "买", "借": "借", "做": "做",
            "送": "送", "给": "给", "批评": "批评", "打碎": "打碎",
            "要": "要", "想要": "想要", "应该": "应该", "让": "让", "请": "请",
            "比": "比", "下": "下", "下雨": "下雨", "进步": "进步",
        }

        # 动宾绑定（动词后应接名词宾语的动词）
        self.vn_bindings = {
            "有", "会", "能", "喜欢", "爱",
            "读", "唱", "踢", "打", "擦",
            "买", "借", "做", "送", "给",
            "下", "下雨",
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

        if start_idx + 1 < n:
            next_word = pos_tags[start_idx + 1][0]
            combined = current_word + next_word
            if combined in self.known_words:
                return combined, 2

        return current_word, 1

    def _get_noun_tokens(self, pos_tags: List[Tuple]) -> List[str]:
        """提取所有名词token，合并连续的单字名词"""
        result = []
        i = 0
        n = len(pos_tags)
        while i < n:
            w, p = pos_tags[i]
            if p in {"N", "PN"}:
                merged = w
                if i + 1 < n and pos_tags[i + 1][1] in {"N", "PN"}:
                    next_word = pos_tags[i + 1][0]
                    combined = w + next_word
                    if combined in self.known_words:
                        merged = combined
                        i += 2
                        result.append(merged)
                        continue
                    elif len(w) == 1 and len(next_word) == 1:
                        excluded = {"一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
                                   "个", "只", "条", "本", "次", "把", "根", "位", "名", "第", "几"}
                        if w not in excluded and next_word not in excluded:
                            merged = combined
                            i += 2
                            result.append(merged)
                            continue
                result.append(merged)
                i += 1
            elif p == "NUM" and w == "第":
                i += 1
            else:
                i += 1
        return result

    def _extract_noun_phrase(self, pos_tags: List[Tuple], start_idx: int) -> Tuple[str, int]:
        """提取名词短语（一直合并到非名词为止），返回 (名词短语, 跳过的token数)"""
        n = len(pos_tags)
        words = []
        i = start_idx
        while i < n:
            w, p = pos_tags[i]
            if p in {"N", "PN", "NUM"}:
                # 尝试合并下一个名词
                if i + 1 < n:
                    nw, np_ = pos_tags[i + 1]
                    if np_ in {"N", "PN"}:
                        combined = w + nw
                        if combined in self.known_words:
                            words.append(combined)
                            i += 2
                            continue
                        elif len(w) == 1 and len(nw) == 1:
                            words.append(w + nw)
                            i += 2
                            continue
                words.append(w)
                i += 1
            elif p == "ADJ" and words:
                # 形容词+名词：尝试合并
                if i + 1 < n:
                    nw, np_ = pos_tags[i + 1]
                    if np_ in {"N", "PN"}:
                        combined = w + nw
                        if combined in self.known_words:
                            words.append(combined)
                            i += 2
                            continue
                        elif len(w) == 1 and len(nw) == 1:
                            words.append(w + nw)
                            i += 2
                            continue
                words.append(w)
                i += 1
            else:
                break
        return "".join(words), len(words)

    # ========== 抽取函数 ==========

    def _extract_sv(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主谓句：处理 S-V / S-V-O 结构，提取动宾关系
        支持：
        - 标准动宾：妈妈去超市买菜
        - 双宾语句：老师给我一本书
        - 比较句：爸爸比妈妈高
        """
        entities = []
        relations = []

        n = len(pos_tags)
        if n == 0:
            return {"entities": entities, "relations": relations, "events": []}

        # 找主语（第一个名词/代词）
        subj_idx = None
        for i, (w, p) in enumerate(pos_tags):
            if p in {"N", "PN"} and w not in {"第", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"}:
                subj_idx = i
                break

        if subj_idx is None:
            return {"entities": entities, "relations": relations, "events": []}


        subject = pos_tags[subj_idx][0]
        # 合并相邻名词作为主语
        if subj_idx + 1 < n and pos_tags[subj_idx + 1][1] in {"N", "PN"}:
            combined = subject + pos_tags[subj_idx + 1][0]
            if combined in self.known_words:
                subject = combined
                subj_idx += 1
        entities.append({"name": subject, "type": "实体", "mentions": [subject]})


        # 跳过修饰词找动词/介词
        verb_idx = subj_idx + 1
        while verb_idx < n and pos_tags[verb_idx][1] in {"NUM", "Q"}:
            verb_idx += 1

        verb = None
        while verb_idx < n:
            wv, pv = pos_tags[verb_idx]
            if pv == "V" or (wv == "给" and pv == "P"):
                verb = wv
                break
            elif pv in {"N", "PN", "ADJ"}:
                # 遇到名词停止
                break
            verb_idx += 1

        # 特殊动词恢复：某些动词被POS标注器误标为N，但实际是V
        # 在"代词+动词+代词+名词"模式中，动词位置的N应视为V
        if not verb and verb_idx < n:
            wv, pv = pos_tags[verb_idx]
            if pv == "N" and wv in {"教", "送", "告诉", "叫", "让", "请"}:
                verb = wv

        if not verb:
            # 描写句：X很ADJ → 提取为主谓关系
            for j in range(subj_idx + 1, n):
                wj, pj = pos_tags[j]
                if pj == "ADV" and wj == "很":
                    # 找后面的形容词
                    adj_parts = []
                    for k in range(j + 1, n):
                        wk, pk = pos_tags[k]
                        if pk == "ADJ":
                            adj_parts.append(wk)
                        elif pk == "ADV":
                            continue
                        else:
                            break
                    if adj_parts:
                        adj = "".join(adj_parts)
                        relations.append({"subject": subject, "relation": f"很{adj}", "object": adj})
                        entities.append({"name": adj, "type": "性质", "mentions": [adj]})
                    return {"entities": entities, "relations": relations, "events": []}

            # 比较句：X比Y Adj → (X, 比Y, Adj)
            for j in range(subj_idx + 1, n):
                wj, pj = pos_tags[j]
                if wj == "比" and j + 2 < n:
                    # 找比后面的名词（被比较的对象）
                    target_parts = []
                    k = j + 1
                    while k < n:
                        wk, pk = pos_tags[k]
                        if pk in {"N", "PN"}:
                            target_parts.append(wk)
                            k += 1
                        else:
                            break
                    # 找形容词
                    adj_parts = []
                    for k2 in range(k, n):
                        wk2, pk2 = pos_tags[k2]
                        if pk2 == "ADJ":
                            adj_parts.append(wk2)
                        elif pk2 == "ADV":
                            continue
                        else:
                            break
                    if target_parts and adj_parts:
                        target = "".join(target_parts)
                        adj = "".join(adj_parts)
                        verb_rel = "比" + target
                        entities.append({"name": target, "type": "对象", "mentions": [target]})
                        entities.append({"name": adj, "type": "性质", "mentions": [adj]})
                        relations.append({"subject": subject, "relation": verb_rel, "object": adj})
                    return {"entities": entities, "relations": relations, "events": []}

            return {"entities": entities, "relations": relations, "events": []}

        # 双宾语句：给/送/教 X Y
        if verb in {"给", "送", "教", "告诉"}:
            obj_idx = verb_idx + 1
            while obj_idx < n and pos_tags[obj_idx][1] in {"NUM", "Q"}:
                obj_idx += 1
            obj_parts = []
            for j in range(obj_idx, n):
                wj, pj = pos_tags[j]
                if pj in {"N", "PN"}:
                    obj_parts.append(wj)
                elif pj in {"NUM", "Q"}:
                    continue
                else:
                    break
            if len(obj_parts) >= 2:
                # 格式：主语+送+间接宾语(人)+直接宾语(物)
                first_obj = obj_parts[0]  # 通常是"我"等人称
                # 直接宾语可能是多个字（合并）
                second_obj = "".join(obj_parts[1:])
                entities.append({"name": first_obj, "type": "人物", "mentions": [first_obj]})
                entities.append({"name": second_obj, "type": "事物", "mentions": [second_obj]})
                if verb == "给":
                    relations.append({"subject": subject, "relation": f"给{first_obj}", "object": second_obj})
                else:
                    relations.append({"subject": subject, "relation": f"{verb}{first_obj}", "object": second_obj})
            return {"entities": entities, "relations": relations, "events": []}

        # 收集宾语
        obj_idx = verb_idx + 1
        while obj_idx < n and pos_tags[obj_idx][1] in {"NUM", "Q"}:
            obj_idx += 1

        obj_parts = []
        for j in range(obj_idx, n):
            wj, pj = pos_tags[j]
            if pj in {"N", "PN"}:
                obj_parts.append(wj)
            elif pj == "ADJ":
                obj_parts.append(wj)
            else:
                break

        if not obj_parts:
            return {"entities": entities, "relations": relations, "events": []}

        obj = "".join(obj_parts)
        verb_rel = self.verb_relation_map.get(verb, verb)

        # 动宾合并：保留关系为动宾短语，宾语保持为名词本身
        if verb in self.vn_bindings:
            vn = verb + obj_parts[0]
            if vn in self.known_words or (len(verb) == 1 and len(obj_parts[0]) <= 3):
                verb_rel = vn  # 关系用动宾短语

        entities.append({"name": obj, "type": "事物", "mentions": [obj]})
        relations.append({"subject": subject, "relation": verb_rel, "object": obj})

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_svc(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主系表：处理 "X是Y的Z" 结构"""
        entities = []
        relations = []

        copula_idx = None
        for i, (w, p) in enumerate(pos_tags):
            if p == "V_COP":
                copula_idx = i
                break

        if not copula_idx or copula_idx == 0 or copula_idx >= len(pos_tags) - 1:
            return {"entities": entities, "relations": relations, "events": []}

        # 提取主语：合并系动词前的连续名词
        # 找主语范围（从copula往前，合并相邻的名词/形容词）
        subj_start = copula_idx - 1
        while subj_start > 0 and pos_tags[subj_start][1] in {"N", "PN", "ADJ"}:
            # 如果前一个字也是名/形，尝试合并
            if subj_start > 0 and pos_tags[subj_start - 1][1] in {"N", "PN", "ADJ"}:
                prev_word = pos_tags[subj_start - 1][0]
                curr_word = pos_tags[subj_start][0]
                combined = prev_word + curr_word
                # 检查这个组合是否在词典或已知词中
                if combined in self.known_words or len(curr_word) == 1:
                    subj_start -= 1
                else:
                    break
            else:
                break

        subject = "".join([w for w, p in pos_tags[subj_start:copula_idx]])
        # 进一步合并：检查subject末尾的字是否能和已知词合并
        if subject not in self.known_words and len(subject) >= 2:
            for k in self.known_words:
                if len(k) >= 2 and k.endswith(subject[-2:]):
                    # 找到了以subject结尾的已知词，尝试扩展
                    prefix = k[:-len(subject[-2:])]
                    if prefix in {"".join([w for w, p in pos_tags[:subj_start]])}:
                        subject = k
                        break
                    # 简化：直接检查k的前两个字是否匹配
                    if len(subject) >= 2 and k.startswith(subject[:2]):
                        subject = k
                        break

        copula_word = pos_tags[copula_idx][0]
        after_copula = pos_tags[copula_idx + 1:]

        entities.append({"name": subject, "type": "人物", "mentions": [subject]})

        if copula_word == "是":
            de_idx = None
            for i, (w, p) in enumerate(after_copula):
                if w == "的":
                    de_idx = i
                    break

            if de_idx is not None and de_idx > 0:
                # X是Y的Z
                y_tokens = after_copula[:de_idx]
                z_tokens = after_copula[de_idx + 1:]

                y_name, _ = self._merge_noun_block(y_tokens, 0)

                z_name = ""
                for idx, (w, p) in enumerate(z_tokens):
                    if w == "第" or w in {"一", "二", "三", "四", "五", "六", "七", "八", "九", "十"}:
                        continue
                    if p in {"NUM", "Q"}:
                        continue
                    if p in {"N", "ADJ"}:
                        if z_name:
                            combined = z_name + w
                            if combined in self.known_words:
                                z_name = combined
                            elif len(z_name) == 1 and len(w) == 1:
                                z_name += w
                            else:
                                z_name += w
                        else:
                            z_name = w
                    else:
                        break

                if not z_name:
                    for w, p in z_tokens:
                        if p in {"N", "ADJ"} and w not in {"第", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"}:
                            z_name = w
                            break

                if y_name and z_name:
                    entities.append({"name": y_name, "type": "人物", "mentions": [y_name]})
                    relations.append({
                        "subject": subject,
                        "relation": z_name,
                        "object": y_name
                    })
                    reverse_rel = self._get_reverse_relation(z_name)
                    if reverse_rel and reverse_rel != z_name:
                        relations.append({
                            "subject": y_name,
                            "relation": reverse_rel,
                            "object": subject
                        })
                    return {"entities": entities, "relations": relations, "events": []}
            else:
                # 简单判断句：X是Y
                if after_copula:
                    first_word = after_copula[0][0]
                    first_pos = after_copula[0][1]
                    if first_pos in {"N", "PN"}:
                        noun_phrase, skip = self._extract_noun_phrase(after_copula, 0)
                        if noun_phrase and noun_phrase != subject:
                            entities.append({"name": noun_phrase, "type": "描述", "mentions": [noun_phrase]})
                            relations.append({"subject": subject, "relation": "是", "object": noun_phrase})
        else:
            nouns = self._get_noun_tokens(after_copula)
            if nouns:
                complement = nouns[0]
                if complement:
                    entities.append({"name": complement, "type": "实体", "mentions": [complement]})
                    relations.append({"subject": subject, "relation": "像", "object": complement})

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_svo(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """主谓宾：处理 N-V-N 模式，支持动宾合并"""
        entities = []
        relations = []

        i = 0
        n = len(pos_tags)
        while i < n:
            w1, p1 = pos_tags[i]
            if p1 not in {"N", "PN"}:
                i += 1
                continue

            # 合并相邻名词作为主语
            subject = w1
            if i + 1 < n and pos_tags[i + 1][1] in {"N", "PN"}:
                combined = w1 + pos_tags[i + 1][0]
                if combined in self.known_words:
                    subject = combined
                    i += 1

            entities.append({"name": subject, "type": "实体", "mentions": [subject]})

            # 跳过 NUM/Q 等修饰词找动词
            verb_idx = i + 1
            while verb_idx < n and pos_tags[verb_idx][1] in {"NUM", "Q"}:
                verb_idx += 1

            verb = None
            while verb_idx < n:
                wv, pv = pos_tags[verb_idx]
                if pv == "V" or (wv == "给" and pv == "P"):
                    verb = wv
                    break
                elif pv in {"N", "PN", "ADJ"}:
                    break
                verb_idx += 1

            if not verb:
                i += 1
                continue

            # 收集宾语
            obj_idx = verb_idx + 1
            while obj_idx < n and pos_tags[obj_idx][1] in {"NUM", "Q"}:
                obj_idx += 1

            obj_parts = []
            indirect_obj = None  # 双宾语：间接宾语（如"我"）
            for j in range(obj_idx, n):
                wj, pj = pos_tags[j]
                if pj in {"N", "PN"}:
                    obj_parts.append(wj)
                elif pj == "ADJ":
                    obj_parts.append(wj)
                elif pj in {"NUM", "Q"}:
                    continue  # 跳过数量词
                else:
                    break

            verb_rel = self.verb_relation_map.get(verb, verb)

            if obj_parts:
                obj = "".join(obj_parts)

                # 双宾语句：给/送/教 X Y → (主语, 给X, Y) + (X, 收到, Y)
                if verb in {"给", "送", "教", "告诉"} and len(obj_parts) >= 2:
                    first_obj = obj_parts[0]
                    second_obj = obj_parts[1]
                    entities.append({"name": first_obj, "type": "人物", "mentions": [first_obj]})
                    entities.append({"name": second_obj, "type": "事物", "mentions": [second_obj]})
                    relations.append({"subject": subject, "relation": f"给{first_obj}", "object": second_obj})
                    # 逆关系
                    if first_obj != second_obj:
                        relations.append({"subject": first_obj, "relation": f"收到自{subject}", "object": second_obj})
                else:
                    # 动宾合并：保留关系为动宾短语，但宾语保持为名词本身
                    if verb in self.vn_bindings and len(obj_parts) >= 1:
                        vn = verb + obj_parts[0]
                        if vn in self.known_words or (len(verb) == 1 and len(obj_parts[0]) <= 3):
                            verb_rel = vn  # 关系用动宾短语
                            # 宾语保持为名词（不用vn覆盖）
                    entities.append({"name": obj, "type": "事物", "mentions": [obj]})
                    relations.append({"subject": subject, "relation": verb_rel, "object": obj})



            i += 1

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_sv_v(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """连动句/能力句：处理 "X带Y去Z" 和 "X会V" 结构"""
        entities = []
        relations = []

        # 判断是哪种子类型：找动词
        verbs = [(w, p) for w, p in pos_tags if p == "V"]
        if len(verbs) >= 2 and verbs[0][0] in {"会", "能", "敢", "会", "能"}:
            # 能力句：X会V / X能V
            ability_v = verbs[0][0]
            action_v = verbs[1][0]
            subj = None
            for w, p in pos_tags:
                if p in {"N", "PN"}:
                    subj = w
                    break
            if subj:
                verb_rel = ability_v + action_v
                entities.append({"name": subj, "type": "实体", "mentions": [subj]})
                entities.append({"name": action_v, "type": "动作", "mentions": [action_v]})
                relations.append({"subject": subj, "relation": verb_rel, "object": action_v})
            return {"entities": entities, "relations": relations, "events": []}

        # 原有的带Y去Z结构
        agent = None
        patients = []

        for i, (w, p) in enumerate(pos_tags):
            if w in {"带", "带着"} and i > 0:
                agent = pos_tags[i - 1][0]

                j = i + 1
                while j < len(pos_tags):
                    tw, tp = pos_tags[j]
                    if tp == "PUNCT" or tw == "着":
                        j += 1
                        continue
                    if tw in {"去", "到"}:
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
                        continue
                    j += 1

        if agent:
            entities.append({"name": agent, "type": "人物", "mentions": [agent]})
            for p in patients:
                if p != agent:
                    entities.append({"name": p, "type": "人物", "mentions": [p]})
                    relations.append({"subject": agent, "relation": "带着", "object": p})

        return {"entities": entities, "relations": relations, "events": []}

    def _extract_sv_v_ability(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """能力句：处理 X会V 模式，X是主语，V是动词宾语"""
        entities = []
        relations = []

        # 找第一个名词作为主语
        subj = None
        for w, p in pos_tags:
            if p in {"N", "PN"} and w not in {"第", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"}:
                subj = w
                break
        if not subj:
            return {"entities": entities, "relations": relations, "events": []}

        # 收集所有动词
        verbs = []
        for w, p in pos_tags:
            if p == "V":
                verbs.append(w)

        if len(verbs) >= 2:
            # 两个动词：第一个是能愿动词
            ability_v = verbs[0]
            action_v = verbs[1]
            verb_rel = ability_v + action_v
            entities.append({"name": subj, "type": "实体", "mentions": [subj]})
            entities.append({"name": action_v, "type": "动作", "mentions": [action_v]})
            relations.append({"subject": subj, "relation": verb_rel, "object": action_v})
        elif len(verbs) == 1:
            verb_rel = verbs[0]
            entities.append({"name": subj, "type": "实体", "mentions": [subj]})
            relations.append({"subject": subj, "relation": verb_rel, "object": ""})

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
                # 合并宾语
                obj_phrase, _ = self._extract_noun_phrase(pos_tags, i + 1)
                verb_idx = i + 1
                while verb_idx < len(pos_tags) and pos_tags[verb_idx][1] not in {"V", "N"}:
                    verb_idx += 1
                verb = pos_tags[verb_idx][0] if verb_idx < len(pos_tags) else "做"
                entities.append({"name": agent, "type": "人物", "mentions": [agent]})
                entities.append({"name": obj_phrase, "type": "事物", "mentions": [obj_phrase]})
                relations.append({"subject": agent, "relation": f"把{obj_phrase}{verb}", "object": verb})
        return {"entities": entities, "relations": relations, "events": []}

    def _extract_bei(self, tree: Dict, pos_tags: List[Tuple[str, str]]) -> Dict:
        """被字句"""
        entities = []
        relations = []
        for i, (w, p) in enumerate(pos_tags):
            if w == "被" and i > 0 and i + 2 < len(pos_tags):
                patient = pos_tags[i - 1][0]
                agent = pos_tags[i + 1][0]
                verb_idx = i + 2
                while verb_idx < len(pos_tags) and pos_tags[verb_idx][1] not in {"V", "N"}:
                    verb_idx += 1
                verb = pos_tags[verb_idx][0] if verb_idx < len(pos_tags) else "做"
                entities.append({"name": patient, "type": "事物", "mentions": [patient]})
                entities.append({"name": agent, "type": "人物", "mentions": [agent]})
                relations.append({"subject": agent, "relation": f"把{patient}{verb}", "object": verb})
        return {"entities": entities, "relations": relations, "events": []}

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
            "表妹": "表姐",
            "表姐": "表妹",
            "妹妹": "姐姐",
        }
        return reverse_map.get(relation, "")