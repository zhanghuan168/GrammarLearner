"""
主程序 - 小学语法学习的演绎推理模型
"""

from grammar.word_classes import WordClassKB
from grammar.sentence_structs import SentenceStructKB
from parser.tokenizer import ChineseTokenizer
from parser.pos_tagger import POSTagger
from parser.syntactic_parser import SyntacticParser
from kb.fact_kb import FactKB
from kb.rule_engine import RuleEngine
from qa.question_parser import QuestionParser
from qa.answer_generator import AnswerGenerator


class GrammarLearner:
    """主模型：语法学习 + 知识理解 + 问答"""

    def __init__(self):
        # 词类知识库
        self.word_class_kb = WordClassKB()
        # 句式知识库
        self.sentence_kb = SentenceStructKB()
        # 事实知识库（动态扩充）
        self.fact_kb = FactKB()
        # 规则引擎
        self.rule_engine = RuleEngine()
        # 解析器
        self.tokenizer = ChineseTokenizer()
        self.pos_tagger = POSTagger(self.word_class_kb)
        self.parser = SyntacticParser(self.sentence_kb)
        # 问答
        self.question_parser = QuestionParser()
        self.answer_generator = AnswerGenerator(self.fact_kb)

    def learn(self, text):
        """
        学习文本，抽取知识入库
        """
        # 预处理：清理空白
        text = ' '.join(text.split())

        # 1. 分词
        tokens = self.tokenizer.tokenize(text)
        print(f"  [分词] {' / '.join(tokens)}")

        # 2. 词性标注
        pos_tags = self.pos_tagger.tag(tokens)
        print(f"  [词性] {' '.join([f'{w}({p})' for w,p in pos_tags])}")

        # 3. 句法分析
        tree = self.parser.parse(pos_tags)
        print(f"  [句法] {tree['type']} - {tree['pattern']}")
        print(f"  [成分] {tree['constituents']}")

        # 4. 事实抽取
        facts = self.rule_engine.extract_facts(tree, pos_tags)
        print(f"  [事实] 实体:{len(facts['entities'])} 关系:{len(facts['relations'])} 事件:{len(facts['events'])}")

        # 5. 存入知识库
        for entity in facts.get("entities", []):
            self.fact_kb.add_entity(entity)
        for relation in facts.get("relations", []):
            self.fact_kb.add_relation(relation)
        for event in facts.get("events", []):
            self.fact_kb.add_event(event)

        return {
            "tokens": tokens,
            "pos_tags": pos_tags,
            "tree": tree,
            "facts": facts
        }

    def learn_batch(self, texts):
        """批量学习多段文本"""
        for text in texts:
            self.learn(text)
            print()
        return None

    def query(self, question):
        """问答"""
        qtype, entity = self.question_parser.parse(question)
        print(f"  [问题解析] 类型:{qtype} 实体:{entity}")

        answer = self.answer_generator.generate(qtype, entity, question)
        return {
            "question": question,
            "type": qtype,
            "entity": entity,
            "answer": answer
        }


def demo_xiyouji():
    """西游记演示"""
    print("=" * 70)
    print("【项目演示：GrammarLearner - 小学语法顺序学习的演绎推理模型】")
    print("=" * 70)

    model = GrammarLearner()

    # 学习西游记片段
    print("\n📚 第一阶段：学习西游记片段")
    print("-" * 70)

    texts = [
        "孙悟空是唐僧的徒弟，会七十二变和筋斗云。",
        "猪八戒是孙悟空的师弟，喜欢吃西瓜和睡觉。",
        "沙僧是唐僧的第三个徒弟，住在流沙河。",
        "唐僧带着孙悟空猪八戒沙僧去西天取经。",
        "观音菩萨帮助唐僧收了三个徒弟。"
    ]

    model.learn_batch(texts)

    # 问答测试
    print("\n" + "=" * 70)
    print("🗣️ 第二阶段：知识问答")
    print("-" * 70)

    questions = [
        "孙悟空是谁？",
        "猪八戒是谁？",
        "沙僧是谁？",
        "孙悟空的师弟是谁？",
        "唐僧带着谁去取经？",
        "观音菩萨做了什么？"
    ]

    for q in questions:
        print(f"\n问: {q}")
        result = model.query(q)
        print(f"答: {result['answer']}")


def demo_grammar_stages():
    """小学语法6阶段演示"""
    print("\n" + "=" * 70)
    print("📖 第三阶段：小学语法6阶段学习")
    print("-" * 70)

    model = GrammarLearner()

    # Stage 1: 词性识别
    print("\n【Stage 1: 词性识别】")
    s1_texts = [
        "小猫睡觉",
        "爸爸上班",
        "苹果很红"
    ]
    model.learn_batch(s1_texts)

    # Stage 2: 简单句结构
    print("\n【Stage 2: 简单句结构】")
    s2_texts = [
        "我读书。",
        "小明打篮球。",
        "妈妈做饭。"
    ]
    model.learn_batch(s2_texts)

    # Stage 3: 句式变换
    print("\n【Stage 3: 句式变换 - 把字句/被字句】")
    s3_texts = [
        "我把门打开。",
        "门被我打开。",
        "妈妈把衣服洗了。"
    ]
    model.learn_batch(s3_texts)

    # Stage 4: 修辞手法
    print("\n【Stage 4: 修辞手法 - 比喻/拟人】")
    s4_texts = [
        "月亮像圆盘。",
        "小鸟在唱歌。",
        "日子像流水。"
    ]
    model.learn_batch(s4_texts)

    # Stage 5: 复杂句
    print("\n【Stage 5: 复杂句 - 因果/条件】")
    s5_texts = [
        "因为下雨，所以不去学校。",
        "如果你努力，就会成功。",
        "虽然难，但是有用。"
    ]
    model.learn_batch(s5_texts)


def demo_new_knowledge():
    """演示：未见过的知识快速理解"""
    print("\n" + "=" * 70)
    print("🚀 第四阶段：未见过的知识（验证动态扩充）")
    print("-" * 70)

    model = GrammarLearner()

    print("\n模型没有读过《三国演义》，现在输入一段文字...")
    new_text = "刘备是蜀国的皇帝，关羽和张飞是他的结拜兄弟。关羽千里走单骑，守护嫂子。张飞在长坂坡一声怒吼，吓退曹军。诸葛亮是刘备的军师，住在隆中。"
    print(f"输入: {new_text}")
    print()

    model.learn(new_text)
    print()

    questions = [
        "刘备是谁？",
        "关羽是谁？",
        "张飞做了什么？",
        "诸葛亮是谁？",
        "关羽和张飞是什么关系？"
    ]

    print("-" * 70)
    print("问答：")
    for q in questions:
        print(f"\n问: {q}")
        result = model.query(q)
        print(f"答: {result['answer']}")


if __name__ == "__main__":
    demo_xiyouji()
    demo_grammar_stages()
    demo_new_knowledge()