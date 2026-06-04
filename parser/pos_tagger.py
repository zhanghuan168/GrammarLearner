"""
词性标注器 - 基于规则和词类知识库的词性标注
"""

from grammar.word_classes import WordClassKB


class POSTagger:
    """词性标注器"""

    def __init__(self, word_class_kb=None):
        self.word_class_kb = word_class_kb or WordClassKB()

        # 标点符号映射
        self.punct_map = {
            "，": "PUNCT", "。": "PUNCT", "！": "PUNCT", "？": "PUNCT",
            "、": "PUNCT", "；": "PUNCT", "：": "PUNCT",
            "「": "PUNCT", "」": "PUNCT", "『": "PUNCT", "』": "PUNCT",
            "（": "PUNCT", "）": "PUNCT", "【": "PUNCT", "】": "PUNCT",
            "《": "PUNCT", "》": "PUNCT", "—": "PUNCT", "…": "PUNCT",
            "～": "PUNCT", "·": "PUNCT"
        }

        # 动词词典
        self.verb_set = {
            "是", "有", "会", "能", "可以", "要", "想", "去", "来", "在",
            "看", "读", "写", "做", "吃", "喝", "玩", "睡觉", "学习", "工作",
            "喜欢", "爱", "知道", "打开", "关闭", "拿", "放", "给", "告诉", "问",
            "走", "跑", "跳", "飞", "爬", "游", "变", "变成", "成为",
            "带", "带着", "取得", "取", "经历", "发生", "遇到", "遇见",
            "表扬", "批评", "骂", "打", "伤害", "保护", "帮助", "救",
            "说", "讲", "问", "答", "问", "叫", "让", "请", "派"
        }

        # 形容词词典
        self.adj_set = {
            "大", "小", "高", "矮", "长", "短", "好", "坏", "新", "旧",
            "老", "少", "多", "少", "红", "白", "黑", "绿", "蓝", "黄",
            "漂亮", "美丽", "可爱", "聪明", "勇敢", "善良", "厉害", "强",
            "安静", "热闹", "干净", "脏", "快", "慢", "早", "晚",
            "年轻", "年迈", "穷", "富", "冷", "热", "温", "凉"
        }

        # 数词
        self.num_set = {
            "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
            "百", "千", "万", "亿", "第一", "第二", "第三",
            "两", "几", "些", "每", "各", "半"
        }

        # 量词
        self.quant_set = {
            "个", "只", "条", "本", "次", "把", "根", "朵", "匹", "头",
            "个", "位", "位", "名", "群", "堆", "些", "对", "双",
            "米", "斤", "元", "度", "年", "月", "日", "时", "分钟",
            "层", "间", "座", "辆", "架", "艘", "列", "道", "种", "类"
        }

        # 判断词/系动词
        self.copula_set = {"是", "像", "如", "似", "成为", "变成", "算作"}

    def tag(self, tokens):
        """
        标注词性
        返回: [(token, pos_tag), ...]
        """
        result = []
        for i, token in enumerate(tokens):
            pos = self._get_pos(token, i, tokens)
            result.append((token, pos))
        return result

    def _get_pos(self, word, idx, tokens):
        """获取单词词性"""
        # 1. 标点符号
        if word in self.punct_map:
            return self.punct_map[word]

        # 2. 助词
        if word in {"的", "地", "得"}:
            return "PART"  # 结构助词
        if word in {"了", "着", "过"}:
            return "PART"  # 时态助词
        if word in {"吗", "呢", "啊", "吧", "呀", "嘛", "哦", "哪", "哇"}:
            return "PART"  # 语气助词

        # 3. 数词
        if word in self.num_set:
            return "NUM"

        # 4. 代词
        if word in {"我", "你", "他", "她", "它", "我们", "你们", "他们", "她们", "它们"}:
            return "PN"  # 人称代词
        if word in {"这", "那", "这个", "那个", "这些", "那些", "这里", "那里"}:
            return "PN"  # 指示代词
        if word in {"谁", "什么", "哪", "怎么", "为什么", "多少"}:
            return "QN"  # 疑问代词

        # 5. 介词
        if word in {"在", "向", "往", "从", "到", "对", "把", "被", "给", "跟", "和", "与"}:
            return "P"

        # 6. 连词
        if word in {"因为", "所以", "如果", "但是", "虽然", "而且", "或者", "要么"}:
            return "CONJ"

        # 7. 副词
        if word in {"很", "非常", "太", "最", "极", "特别", "格外", "尤其",
                    "都", "全", "只", "仅仅", "已", "已经", "刚", "正", "将要",
                    "不", "没", "别", "未", "一定", "必须", "当然", "果然"}:
            return "ADV"

        # 8. 判断词
        if word in self.copula_set:
            return "V_COP"

        # 9. 量词（数词后）
        if word in self.quant_set:
            # 检查前一个词是否是数词
            if idx > 0:
                prev_word = tokens[idx - 1]
                prev_pos = self._get_pos(prev_word, idx - 1, tokens)
                if prev_pos == "NUM":
                    return "Q"
            # 或检查是否是"一"之类的数词
            if idx > 0 and tokens[idx - 1] in {"一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "几", "每", "各"}:
                return "Q"
            return "Q"

        # 10. 动词
        if word in self.verb_set:
            return "V"

        # 11. 形容词
        if word in self.adj_set:
            return "ADJ"

        # 12. 其他：查知识库或默认名词
        kb_class = self.word_class_kb.get_class(word)
        if kb_class != "名词":
            return kb_class

        # 13. 默认：名词（可能是专有名词）
        return "N"


def demo():
    tagger = POSTagger()

    test_cases = [
        ["孙悟空", "是", "唐僧", "的", "徒弟"],
        ["我", "去", "图书馆", "看", "书"],
        ["月亮", "像", "圆盘"],
        ["因为", "下雨", "，", "所以", "不去"]
    ]

    print("【词性标注演示】")
    for tokens in test_cases:
        tags = tagger.tag(tokens)
        print(f"  {' / '.join([f'{w}({p})' for w, p in tags])}")


if __name__ == "__main__":
    demo()