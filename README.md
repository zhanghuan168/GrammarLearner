# GrammarLearner

**小学语法顺序学习的演绎推理模型**

基于 ChainFirst 架构思想，将语法规则显式化，使模型能通过很小的计算量理解新知识。

## 核心特性

- **小学语法6阶段学习**：词性→简单句→句式变换→修辞→复杂句→篇章理解
- **动态知识库**：输入新文本（如《西游记》）后自动抽取实体、关系、事件
- **轻量计算**：无神经网络，纯规则匹配，推理极快
- **零样本理解**：模型没读过的文本，输入后可直接问答细节

## 架构

```
输入文本 → 分词 → 词性标注 → 句法分析 → 事实抽取 → 知识库
                                                      ↓
问答输入 → 问题解析 → 知识库查询 → 答案生成 → 输出回答
```

## 安装

```bash
cd grammar-learner
pip install -r requirements.txt  # 仅需 Python 3.7+
```

## 快速开始

```python
from main import GrammarLearner

model = GrammarLearner()

# 学习新文本（模型从未见过）
model.learn("孙悟空是唐僧的徒弟，会七十二变。猪八戒是孙悟空的师弟。")

# 立即可问答
print(model.query("孙悟空是谁？").answer)
# → "孙悟空是实体"

print(model.query("猪八戒的师兄是谁？").answer)
# → "知识库中暂无..."
```

## 项目结构

```
grammar-learner/
├── grammar/               # 语法规则定义
│   ├── word_classes.py    # 词类（名词/动词/形容词/...）
│   └── sentence_structs.py # 句式（主谓/把字/被字/复句/...）
├── parser/               # 解析器
│   ├── tokenizer.py       # 中文分词（最大正向匹配）
│   ├── pos_tagger.py      # 词性标注
│   └── syntactic_parser.py # 句法分析
├── kb/                    # 知识库
│   ├── fact_kb.py         # 事实库（实体/关系/事件）
│   └── rule_engine.py     # 规则引擎
├── qa/                    # 问答
│   ├── question_parser.py  # 问题分类
│   └── answer_generator.py # 答案生成
├── experiments/           # 实验
├── main.py               # 主程序 + 演示
└── DESIGN.md             # 设计文档
```

## 当前状态

✅ 基础功能可运行
⚠️ 实体关系抽取精度待提升（"的"字结构处理较弱）
⏳ 下一步：改进 SVC 句式的事实抽取逻辑

## 计算量对比

| 方案 | 参数量 | 推理FLOPs | 外推能力 |
|------|--------|----------|---------|
| LLM (7B) | 7B | ~30T | 差 |
| LoRA微调 | ~10M | ~30T | 中 |
| **GrammarLearner** | **<1M** | **<1M** | **强** |