# FairCV: 基于统计性歧视理论的大语言模型简历筛选偏见量化研究

本仓库的数据集见：[Hugging Face 上的 FairCV 数据集](https://huggingface.co/datasets/OhMyKing/FairCV)

FairCV 是一个面向大厂AI招聘中语言模型偏见问题的研究项目。本研究将统计性歧视理论引入大语言模型的偏见研究，通过构建大规模模拟简历数据集，系统考察了当前主流大语言模型在性别、年龄、地域等多个维度的偏见表现。

## 🎯 项目概述

FairCV 提供了一个完整的研究框架，包括：
- 构建百万级中文模拟求职者简历数据集
- 评估大语言模型在简历筛选任务中的偏见
- 分析不同人口学特征求职者的评分差异
- 探索通过优化 Prompt 等方式减轻偏见

## 📊 数据集

本项目包含超过140万份模拟简历，覆盖：
- 多个技术岗位（后端、前端、机器学习等）
- 不同招聘类型（校招、社招、专家招聘）
- 各级能力水平（从极低到极高）
- 多样化的人口学属性（性别、年龄、地域等）

数据集已开源在：[Hugging Face 上的 FairCV 数据集](https://huggingface.co/datasets/OhMyKing/FairCV)

## 🛠️ 项目结构

```
FairCV/
├── data/                      # 数据存储目录
├── utils/
│   ├── LLMClient.py          # 大语言模型 API 客户端
│   └── add_information.py    # 信息增强工具
├── generate_cv_template.py    # 简历模板生成脚本
├── judge_resumes.py          # 指标评分实现
├── judge_resumes_simple.py   # 直接评分实现
├── add_information.py        # 信息添加脚本
└── analyze_data.ipynb        # 数据分析笔记本
```

## 🚀 主要功能

1. **简历生成**
   - 基于模板的简历生成
   - 可配置的属性和技能
   - 真实的内容模拟

2. **偏见评估**
   - 直接打分方法
   - 多维度评估框架
   - 统计显著性检验

3. **分析工具**
   - 人口统计学偏见分析
   - 统计检验框架
   - 可视化工具

## 📋 环境要求

- Python 3.11+
- 依赖包：
  ```bash
  pip install pandas numpy scipy statsmodels matplotlib seaborn tqdm
  ```
- 大语言模型 API 访问权限（支持：智谱AI、Ollama）

## 🔧 使用说明

1. **生成简历模板**
```python
python generate_cv_template.py
```

2. **评估简历**
```python
# 直接打分评估
python judge_resumes_simple.py

# 指标打分评估
python judge_resumes.py
```

3. **分析结果**
- 在 Jupyter Notebook/Lab 中打开 `analyze_data.ipynb`
- 按照分析流程进行操作

## 📊 主要发现

研究发现大语言模型在简历筛选中存在多个维度的偏见：
- 性别因素对评分存在影响，但可通过优化 Prompt 缓解
- 年龄相关的偏见在不同招聘场景中表现不同
- 地域因素对评分的影响相对有限
- 基于框架的评估比直接打分表现出更少的偏见

## 🤝 贡献指南

欢迎贡献！你可以：
1. Fork 本仓库
2. 创建特性分支
3. 提交 Pull Request

## 📧 联系方式

如有问题或反馈，请：
- 在仓库中提出 Issue
- 联系项目维护者：
  - 王殿云
  - 2022211733@bupt.cn


---

*为 AI 招聘公平性而努力 ❤️*