# GrammarLearner - 小学语法顺序学习的演绎推理模型

## 核心设计思想

参考演绎层 v8 的 ChainFirst 架构，将"语法规则"显式化存储，
使模型能通过规则匹配理解新知识，而非依赖海量参数记忆。

## 三层架构

```
┌─────────────────────────────────────────────────────┐
│  QA Interface          问答界面（对话/询问细节）      │
├─────────────────────────────────────────────────────┤
│  Knowledge Extractor   知识抽取（词性→句法→语义）      │
├─────────────────────────────────────────────────────┤
│  Grammar KB            语法知识库（显式规则 + 事实）   │
│  ├─ word_classes       词类（名词/动词/形容词/...）   │
│  ├─ sentence_structs   句式（主谓/把字/被字/...）      │
│  ├─ rules              规则库（组合规则）              │
│  └─ facts              事实库（实体/关系/事件）         │
└─────────────────────────────────────────────────────┘
```

## 小学语法学习顺序（6阶段）

### Stage 1: 词性识别（1-2年级）
```
输入：「小猫 睡觉」  →  词类标注
输出：名词[小猫] 动词[睡觉]

规则示例：
  - 如果词出现在主语位置 → 名词性成分
  - 如果词表示动作 → 动词
  - 如果词描述状态 → 形容词
```

### Stage 2: 简单句结构（2年级）
```
输入：「小猫睡觉」  →  句法分析
输出：主语[小猫] + 谓语[睡觉]

规则示例：
  - 主语 + 谓语 → 陈述句
  - 主语 + 谓语 + 宾语 → 主谓宾句
```

### Stage 3: 句式变换（3年级）
```
输入：「我把门打开」  →  转换
输出：门被我打开

规则示例：
  - [人]把[物][动作] → [物]被[人][动作]
```

### Stage 4: 修辞手法（4年级）
```
输入：「月亮像圆盘」  →  修辞识别
输出：比喻（明喻）

规则示例：
  - [A]像[B] → 明喻
  - [物]会[人事] → 拟人
```

### Stage 5: 复杂句（5-6年级）
```
输入：「因为下雨，所以取消比赛」
输出：因果复句：原因[下雨] → 结果[取消比赛]

规则示例：
  - 因为[原因]，所以[结果] → 因果关系
  - 如果[条件]，就[结果] → 条件关系
```

### Stage 6: 篇章理解（6年级）
```
输入：西游记片段
输出：
  - 人物：孙悟空、唐僧、猪八戒、沙僧
  - 事件：大闹天宫、取经路
  - 关系：师徒、主从

QA能力：
  问：孙悟空是谁？→ 答：唐僧的徒弟，会七十二变...
  问：大闹天宫是谁？→ 答：孙悟空...
```

## 知识库结构

```python
# 语法规则（演绎层核心）
grammar_rules = {
    "noun_subject": {
        "pattern": ["NN", "PN"],
        "position": "subject",
        "action": "mark_as_noun_phrase"
    },
    "sv_pattern": {
        "pattern": ["NP", "VP"],
        "structure": "subject + predicate",
        "sentence_type": "declarative"
    },
    "ba_construction": {
        "pattern": ["NP1", "把", "NP2", "VP"],
        "structure": "施事 + 把 + 受事 + 动作",
        "transform_to_passive": "NP2 + 被 + NP1 + VP"
    }
}

# 事实库（动态扩充）
fact_kb = {
    "entity": {
        "孙悟空": {"type": "人物", "attribute": {"身份": "唐僧徒弟", "武器": "金箍棒", "技能": ["七十二变", "筋斗云"]}},
        "西游记": {"type": "作品", "作者": "吴承恩", "人物": ["孙悟空", "唐僧", "猪八戒", "沙僧"]}
    },
    "relation": {
        ("孙悟空", "师父"): "唐僧",
        ("猪八戒", "师弟"): "孙悟空"
    },
    "event": {
        "大闹天宫": {"主角": "孙悟空", "结果": "被压五行山"}
    }
}
```

## 核心算法

### 1. 规则匹配引擎（轻量计算）
```python
def parse(sentence, grammar_kb):
    # Step 1: 词性标注（小词表 + 规则）
    pos_tags = pos_tag(sentence, grammar_kb)
    
    # Step 2: 句法分析（规则匹配，非神经网络）
    tree = match_rules(pos_tags, grammar_kb)
    
    # Step 3: 语义抽取（事实入库）
    facts = extract_facts(tree, fact_kb)
    
    return {"parse_tree": tree, "facts": facts}
```

### 2. 规则归纳（两阶段训练，来自v8）
```python
# Stage 1: 从语料归纳规则（符号层）
rules = induce_rules(grammar_examples)

# Stage 2: 适配具体知识（微调层）
adapt_rules(rules, domain_knowledge)
```

### 3. 知识问答
```python
def answer(question, fact_kb):
    # 解析问题类型
    q_type = classify_question(question)  # 谁/什么/哪里/为什么
    
    # 规则匹配答案
    if q_type == "WHO":
        return lookup_entity(question, fact_kb)
    elif q_type == "WHAT_HAPPENED":
        return lookup_event(question, fact_kb)
```

## 计算量优势

| 方案 | 参数量 | 推理FLOPs | 外推能力 |
|------|--------|----------|---------|
| LLM (7B) | 7B | ~30T | 差 |
| LoRA微调 | 7B+ | ~30T | 中 |
| **GrammarLearner** | **<10M** | **<1G** | **强** |

## 文件结构

```
grammar-learner/
├── grammar/              # 语法规则定义
│   ├── word_classes.py   # 词类规则
│   ├── sentence_structs.py  # 句式规则
│   └── patterns.py       # 组合模式
├── parser/               # 解析器
│   ├── tokenizer.py      # 分词
│   ├── pos_tagger.py     # 词性标注
│   ├── parser.py         # 句法分析
│   └── semantic.py       # 语义抽取
├── kb/                    # 知识库
│   ├── grammar_kb.py     # 语法知识库
│   ├── fact_kb.py        # 事实知识库
│   └── rules.py          # 规则引擎
├── qa/                    # 问答模块
│   ├── question_parser.py  # 问题解析
│   ├── answer_generator.py # 答案生成
│   └── dialogue.py       # 对话管理
├── experiments/           # 实验
│   └── stage1_basic.py   # Stage 1实验
└── main.py               # 入口
```

## 命名

- **Deductive（演绎）** ↔ **Inductive（归纳）** + **Grammar（语法）**
- 项目名：**GrammarInductive** 或 **SyntacticReasoner**
- 核心洞察：小学语法的"词→词组→句→段→篇"恰好是人类语言能力的最小完备集