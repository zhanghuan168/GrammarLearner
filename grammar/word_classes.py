"""
词类知识库 - 小学阶段词类定义
参考：名词、动词、形容词、数词、量词、代词、副词、介词、连词、助词、叹词
"""

# 小学阶段必须掌握的词类
WORD_CLASSES = {
    "名词": {
        "abbr": "N",
        "definition": "表示人、事物、地点、抽象概念",
        "subclasses": {
            "人名": ["孙悟空", "唐僧", "老师", "学生"],
            "地名": ["北京", "中国", "学校", "教室"],
            "事物": ["书", "桌子", "电脑", "手机"],
            "抽象": ["爱", "勇气", "智慧", "自由"]
        },
        "position_rules": ["主语", "宾语", "定语"],
        "example": "小明是学生"
    },
    "动词": {
        "abbr": "V",
        "definition": "表示动作、行为、变化、心理活动",
        "subclasses": {
            "动作": ["跑", "跳", "吃", "打"],
            "变化": ["变成", "生长", "死亡", "消失"],
            "心理": ["喜欢", "讨厌", "想念", "担心"],
            "能愿": ["会", "能", "可以", "必须"]
        },
        "position_rules": ["谓语"],
        "example": "小猫睡觉"
    },
    "形容词": {
        "abbr": "ADJ",
        "definition": "表示性质、状态、颜色、形状",
        "subclasses": {
            "性质": ["好", "坏", "大", "小", "高", "矮"],
            "状态": ["安静", "热闹", "干净", "漂亮"],
            "颜色": ["红", "白", "黑", "绿"],
            "形状": ["圆", "方", "长", "短"]
        },
        "position_rules": ["定语", "状语", "谓语"],
        "example": "大苹果"
    },
    "数词": {
        "abbr": "NUM",
        "definition": "表示数目或次序",
        "subclasses": {
            "基数": ["一", "二", "三", "十", "百", "千", "万"],
            "序数": ["第一", "第二", "第三"],
            "分数": ["一半", "三分之一"],
            "倍数": ["两倍", "三倍"]
        },
        "position_rules": ["定语"],
        "example": "三本书"
    },
    "量词": {
        "abbr": "Q",
        "definition": "表示人、事物或动作的单位",
        "subclasses": {
            "个体": ["个", "只", "条", "本", "把"],
            "集体": ["群", "堆", "些", "对"],
            "度量": ["米", "斤", "元", "度"],
            "动作": ["次", "趟", "下", "遍"]
        },
        "position_rules": ["定语（数词后）"],
        "example": "一只猫"
    },
    "代词": {
        "abbr": "PN",
        "definition": "代替名词、形容词或数量词",
        "subclasses": {
            "人称": ["我", "你", "他", "她", "它", "我们"],
            "指示": ["这", "那", "这个", "那个"],
            "疑问": ["谁", "什么", "哪", "怎么"],
            "不定": ["某", "某些", "别人"]
        },
        "position_rules": ["主语", "宾语", "定语"],
        "example": "这是书"
    },
    "副词": {
        "abbr": "ADV",
        "definition": "修饰动词、形容词或其他副词",
        "subclasses": {
            "程度": ["很", "非常", "太", "最", "极"],
            "范围": ["都", "全", "总共", "只"],
            "时间": ["已经", "刚", "正", "将要"],
            "否定": ["不", "没", "别", "未"],
            "语气": ["居然", "竟然", "果然", "当然"]
        },
        "position_rules": ["状语"],
        "example": "非常好"
    },
    "介词": {
        "abbr": "P",
        "definition": "用在名词/代词前，组成介词短语",
        "subclasses": {
            "方向": ["在", "向", "往", "从", "到"],
            "对象": ["对", "把", "被", "给", "跟"],
            "原因": ["因为", "由于", "为了"],
            "时间": ["在", "当", "趁着"]
        },
        "position_rules": ["状语（介词短语）"],
        "example": "在学校学习"
    },
    "连词": {
        "abbr": "CONJ",
        "definition": "连接词、词组或句子",
        "subclasses": {
            "并列": ["和", "与", "以及", "而且"],
            "因果": ["因为", "所以", "因此"],
            "转折": ["但是", "不过", "然而"],
            "条件": ["如果", "只要", "除非"]
        },
        "position_rules": ["连接成分"],
        "example": "因为下雨，所以不去"
    },
    "助词": {
        "abbr": "PART",
        "definition": "附着在其他词上，表示附加意义",
        "subclasses": {
            "结构": ["的", "得", "地"],
            "时态": ["了", "着", "过"],
            "语气": ["吗", "呢", "啊", "吧", "呀"]
        },
        "position_rules": ["附着在其他成分后"],
        "example": "他吃了饭"
    },
    "叹词": {
        "abbr": "INT",
        "definition": "表示感叹、呼唤、应答",
        "subclasses": {
            "感叹": ["啊", "哇", "哎呀", "唉"],
            "呼唤": ["喂", "嘿", "哎"],
            "应答": ["嗯", "好吧", "行"]
        },
        "position_rules": ["独立成句"],
        "example": "哎呀！"
    }
}


class WordClassKB:
    """词类知识库"""

    def __init__(self):
        self.classes = WORD_CLASSES

    def get_class(self, word):
        """根据词语判断词类（规则匹配）"""
        # 1. 检查是否是人名/专有名词（名词）
        for cls_name, cls_info in self.classes.items():
            if word in cls_info.get("subclasses", {}).values():
                return cls_name

        # 2. 规则匹配
        if word in ["的", "得", "地"]:
            return "助词"
        if word in ["了", "着", "过"]:
            return "助词"
        if word in ["吗", "呢", "啊", "吧", "呀"]:
            return "助词"
        if word in ["很", "非常", "太", "最"]:
            return "副词"
        if word in ["不", "没", "别"]:
            return "副词"
        if word in ["和", "因为", "所以", "但是"]:
            return "连词"
        if word in ["在", "对", "把", "被"]:
            return "介词"
        if word in ["我", "你", "他", "她", "它", "我们", "这", "那"]:
            return "代词"
        if word in ["一", "二", "三", "十", "百", "千"]:
            return "数词"
        if word in ["个", "只", "条", "本", "次"]:
            return "量词"
        if word in ["啊", "哇", "哎呀", "喂", "嗯"]:
            return "叹词"

        # 3. 默认按名词处理（未知词）
        return "名词"

    def get_abbr(self, word_class):
        """获取词类缩写"""
        if word_class in self.classes:
            return self.classes[word_class]["abbr"]
        return "N"

    def get_examples(self, word_class):
        """获取词类示例"""
        if word_class in self.classes:
            return self.classes[word_class]["example"]
        return ""


def demo():
    """演示词类识别"""
    kb = WordClassKB()
    words = ["孙悟空", "是", "唐僧", "的", "徒弟", "会", "七十二变"]

    print("【词类识别演示】")
    for word in words:
        cls = kb.get_class(word)
        abbr = kb.get_abbr(cls)
        print(f"  {word} → {cls} ({abbr})")


if __name__ == "__main__":
    demo()