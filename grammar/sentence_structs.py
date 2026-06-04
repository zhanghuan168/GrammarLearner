"""
句式知识库 - 小学阶段句式结构定义
参考：主谓句、把字句、被字句、连动句、兼语句、复句
"""

# 小学阶段必须掌握的句式
SENTENCE_STRUCTS = {
    # ===== 简单句 =====
    "主谓句": {
        "abbr": "SV",
        "pattern": "主语 + 谓语",
        "definition": "主语 + 谓语构成的基本句型",
        "examples": ["小猫睡觉", "爸爸上班", "花开"],
        "rule": "如果句中只有一个主语和一个谓语，且谓语是不及物动词/形容词 → 主谓句"
    },
    "主谓宾句": {
        "abbr": "SVO",
        "pattern": "主语 + 谓语 + 宾语",
        "definition": "主语 + 及物动词 + 宾语",
        "examples": ["我读书", "小明打篮球", "妈妈做饭"],
        "rule": "如果谓语是及物动词，且动词涉及对象 → 主谓宾句"
    },
    "主谓双宾句": {
        "abbr": "SVO2",
        "pattern": "主语 + 谓语 + 间接宾语 + 直接宾语",
        "definition": "动词涉及两个对象（人+物）",
        "examples": ["老师教我们语文", "妈妈给我苹果"],
        "rule": "如果动词需要两个宾语（受益者+承受者）→ 主谓双宾句"
    },
    "主谓补句": {
        "abbr": "SVC",
        "pattern": "主语 + 系动词 + 表语",
        "definition": "主语 + 是/像/成为 + 表语",
        "examples": ["她是学生", "他是医生", "月亮像圆盘"],
        "rule": "如果谓语是判断词/系动词 → 主系表结构"
    },

    # ===== 特殊句式 =====
    "把字句": {
        "abbr": "BA",
        "pattern": "主语 + 把 + 宾语 + 谓语",
        "definition": "用'把'将宾语提前到动词前，强调对宾语的处理",
        "examples": ["我把门打开", "妈妈把衣服洗了", "老师把我们表扬了"],
        "rule": "把字句 = 施事 + 把 + 受事 + 动作\n把字句→被字句：[施事]把[受事][动作] → [受事]被[施事][动作]",
        "transform": {
            "把字句→被字句": lambda s: s.replace("把", "被").replace("把", ""),
            "被字句→把字句": lambda s: s.replace("被", "把")
        }
    },
    "被字句": {
        "abbr": "BEI",
        "pattern": "主语 + 被 + 施事 + 谓语",
        "definition": "用'被'引出施事，强调宾语承受的动作",
        "examples": ["门被我打开", "作业被写完了", "苹果被吃了"],
        "rule": "被字句 = 受事 + 被 + 施事 + 动作"
    },
    "连动句": {
        "abbr": "SV_V",
        "pattern": "主语 + 谓语1 + 宾语1 + 谓语2 + 宾语2",
        "definition": "两个或多个动词短语连用，表示连续动作",
        "examples": ["我去图书馆看书", "他坐下来写字", "妈妈出门买菜"],
        "rule": "如果两个动词短语共享主语，且表示连续动作 → 连动句"
    },
    "兼语句": {
        "abbr": "NP_V_NP",
        "pattern": "主语 + 谓语1 + 兼语 + 谓语2",
        "definition": "第一个动词的宾语同时是第二个动词的主语",
        "examples": ["老师让我们做作业", "妈妈叫我起床", "父亲派他去北京"],
        "rule": "兼语句 = 使令动词(让/叫/请/派) + 人 + 动作"
    },

    # ===== 复句 =====
    "并列复句": {
        "abbr": "COORD",
        "pattern": "分句1 + 和/而且 + 分句2",
        "definition": "两个分句平等并列",
        "examples": ["我看书，他写字", "天很蓝，而且很晴朗"],
        "conjunctions": ["和", "而且", "同时", "并且"]
    },
    "因果复句": {
        "abbr": "CAUSE",
        "pattern": "因为[原因]，所以[结果]",
        "definition": "表示原因和结果的关系",
        "examples": ["因为下雨，所以不去", "因为他努力，所以成功"],
        "conjunctions": ["因为", "所以", "因此", "由于", "因而"]
    },
    "转折复句": {
        "abbr": "TURN",
        "pattern": "虽然[事实1]，但是[事实2]",
        "definition": "后一句与前一句意思相反",
        "examples": ["虽然难，但是有用", "虽然天冷，但是他去了"],
        "conjunctions": ["虽然", "但是", "然而", "不过", "可是"]
    },
    "条件复句": {
        "abbr": "COND",
        "pattern": "如果[条件]，就[结果]",
        "definition": "表示假设条件与结果的关系",
        "examples": ["如果不努力，就会失败", "只要你肯，就一定能成功"],
        "conjunctions": ["如果", "只要", "除非", "无论", "不管"]
    },
    "递进复句": {
        "abbr": "PROG",
        "pattern": "不仅[事实1]，而且[事实2]",
        "definition": "后一分句比前一分句更进一层",
        "examples": ["他不仅聪明，而且努力", "不仅会写，而且会画"],
        "conjunctions": ["不仅", "而且", "还", "甚至"]
    },
    "选择复句": {
        "abbr": "CHOICE",
        "pattern": "或者[选择1]，或者[选择2]",
        "definition": "表示选择关系",
        "examples": ["或者去，或者留，你自己决定"],
        "conjunctions": ["或者", "还是", "要么", "要不"]
    },

    # ===== 修辞（4年级） =====
    "比喻句": {
        "abbr": "META",
        "pattern": "甲像/如/似/像/好像 乙",
        "definition": "用乙事物来描述甲事物，有明喻/暗喻/借喻",
        "examples": ["月亮像圆盘", "长城像巨龙", "日子像流水"],
        "types": {
            "明喻": "像/如/似/好像/仿佛",
            "暗喻": "是/成为/变成",
            "借喻": "直接用乙方代替甲方（需要上下文）"
        }
    },
    "拟人句": {
        "abbr": "PERS",
        "pattern": "[事物]具有人的动作/情感",
        "definition": "把事物当作人来写",
        "examples": ["小鸟在唱歌", "花儿笑", "风在跑"]
    },
    "排比句": {
        "abbr": "PARA",
        "pattern": "三个以上结构相似的分句/词组",
        "definition": "同范围同性质的事物层层推出",
        "examples": ["爱学习，爱劳动，爱祖国"]
    },
    "夸张句": {
        "abbr": "HYPE",
        "pattern": "故意夸大或缩小事物特征",
        "definition": "为了表达需要，故意言过其实",
        "examples": ["气得我头发都竖起来了", "人山人海", "一步登天"]
    }
}


class SentenceStructKB:
    """句式知识库"""

    def __init__(self):
        self.structs = SENTENCE_STRUCTS

    def get_struct(self, tree):
        """根据句法树判断句式类型"""
        pattern = tree.get("pattern", "")

        # 简单判断逻辑（后续可扩展）
        if "把" in pattern:
            return "把字句"
        if "被" in pattern:
            return "被字句"
        if "连动" in pattern:
            return "连动句"
        if "兼语" in pattern:
            return "兼语句"
        if "而且" in pattern or "和" in pattern:
            return "并列复句"
        if "因为" in pattern and "所以" in pattern:
            return "因果复句"
        if "如果" in pattern:
            return "条件复句"
        if "像" in pattern:
            return "比喻句"
        if pattern.count("主语") == 1 and pattern.count("谓语") == 1:
            return "主谓句"
        if pattern.count("主语") == 1 and pattern.count("谓语") == 1 and pattern.count("宾语") == 1:
            return "主谓宾句"
        if pattern.count("主语") == 1 and pattern.count("谓语") == 1 and pattern.count("宾语") == 2:
            return "主谓双宾句"

        return "主谓句"  # 默认

    def transform(self, sentence, from_type, to_type):
        """句式转换"""
        if from_type == "把字句" and to_type == "被字句":
            # 简单的把→被转换
            parts = sentence.split("把")
            if len(parts) == 2:
                front = parts[0]
                back = parts[1]
                # 寻找动词位置
                for i, char in enumerate(back):
                    if char in "了过":
                        obj = back[:i]
                        verb = back[i:]
                        return f"{obj}被{front}{verb}"
                return sentence.replace("把", "被", 1)
        return sentence

    def get_example(self, struct_type):
        """获取句式示例"""
        if struct_type in self.structs:
            return self.structs[struct_type]["examples"]
        return []


def demo():
    """演示句式识别"""
    kb = SentenceStructKB()

    print("【句式识别演示】")
    test_cases = [
        "我把门打开",
        "门被我打开",
        "我去图书馆看书",
        "老师让我们做作业",
        "因为下雨，所以不去"
    ]

    for sent in test_cases:
        print(f"  {sent}")


if __name__ == "__main__":
    demo()