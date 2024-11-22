import re
from enum import Enum
from typing import Dict, List, Tuple
import json
import time
from utils.LLMClient import ZhipuAIClient


class SkillLevel(str, Enum):
    VERY_LOW = "极低"  # 基础能力，适合实习生
    LOW = "低"  # 初级能力，适合应届生
    MEDIUM = "中"  # 中级能力，3-5年经验
    HIGH = "高"  # 高级能力，5-8年经验
    VERY_HIGH = "极高"  # 专家级能力，8年以上经验


class RecruitmentType(str, Enum):
    # 校园招聘
    CAMPUS_TECH = "技术研发类校招"  # 开发、算法等技术岗位
    CAMPUS_PRODUCT = "产品运营类校招"  # 产品、运营、市场等岗位
    CAMPUS_GENERAL = "职能支持类校招"  # 财务、HR、行政等职能岗位

    # 社会招聘
    SOCIAL_DEV = "研发工程师社招"  # 后端、前端、客户端等开发岗位
    SOCIAL_ALGO = "算法工程师社招"  # 机器学习、计算机视觉等算法岗位
    SOCIAL_ARCH = "架构师社招"  # 技术架构、系统架构等岗位
    SOCIAL_PM = "产品经理社招"  # 产品岗位

    # 专项招聘
    SPECIAL_EXPERT = "专家人才计划"  # 技术专家、科学家等高端人才
    SPECIAL_MANAGER = "管理层人才计划"  # 技术管理、产品总监等管理岗位


class TechPosition(str, Enum):
    # 开发岗位
    BACKEND = "后端开发工程师"
    FRONTEND = "前端开发工程师"
    ANDROID = "Android开发工程师"
    IOS = "iOS开发工程师"
    FULLSTACK = "全栈开发工程师"

    # 算法岗位
    ML = "机器学习工程师"
    CV = "计算机视觉工程师"
    NLP = "自然语言处理工程师"
    RECOMMEND = "推荐算法工程师"

    # 架构岗位
    ARCH = "系统架构师"
    SECURITY = "安全架构师"
    DEVOPS = "DevOps架构师"

    # 产品岗位
    PM_TECH = "技术产品经理"
    PM_BUSINESS = "业务产品经理"


def get_applicable_recruitment_types(position: TechPosition) -> List[RecruitmentType]:
    """根据职位确定适用的招聘类型"""
    if position in [
        TechPosition.BACKEND,
        TechPosition.FRONTEND,
        TechPosition.ANDROID,
        TechPosition.IOS,
        TechPosition.FULLSTACK
    ]:
        return [
            RecruitmentType.CAMPUS_TECH,
            RecruitmentType.SOCIAL_DEV
        ]
    elif position in [
        TechPosition.ML,
        TechPosition.CV,
        TechPosition.NLP,
        TechPosition.RECOMMEND
    ]:
        return [
            RecruitmentType.CAMPUS_TECH,
            RecruitmentType.SOCIAL_ALGO,
            RecruitmentType.SPECIAL_EXPERT
        ]
    elif position in [
        TechPosition.ARCH,
        TechPosition.SECURITY,
        TechPosition.DEVOPS
    ]:
        return [
            RecruitmentType.SOCIAL_ARCH,
            RecruitmentType.SPECIAL_EXPERT
        ]
    elif position in [
        TechPosition.PM_TECH,
        TechPosition.PM_BUSINESS
    ]:
        return [
            RecruitmentType.CAMPUS_PRODUCT,
            RecruitmentType.SOCIAL_PM,
            RecruitmentType.SPECIAL_MANAGER
        ]
    else:
        raise ValueError(f"未定义的职位类型：{position}")


def get_applicable_skill_levels(recruitment_type: RecruitmentType) -> List[SkillLevel]:
    """根据招聘类型确定适用的技能等级范围"""
    if recruitment_type in [RecruitmentType.CAMPUS_TECH, RecruitmentType.CAMPUS_PRODUCT]:
        return [SkillLevel.VERY_LOW, SkillLevel.LOW]
    elif recruitment_type in [RecruitmentType.SOCIAL_DEV, RecruitmentType.SOCIAL_ALGO, RecruitmentType.SOCIAL_PM,
                              RecruitmentType.SOCIAL_ARCH]:
        return [SkillLevel.MEDIUM, SkillLevel.HIGH]
    elif recruitment_type in [RecruitmentType.SPECIAL_EXPERT, RecruitmentType.SPECIAL_MANAGER]:
        return [SkillLevel.VERY_HIGH]
    else:
        raise ValueError(f"未定义的招聘类型：{recruitment_type}")


def get_position_requirements(position: TechPosition, level: SkillLevel,
                              recruitment_type: RecruitmentType) -> Dict:
    """根据具体技术岗位、能力等级和招聘类型获取要求"""
    # 定义不同招聘类型下的要求
    requirements = {
        TechPosition.BACKEND: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握Java或Python编程语言", "了解基础的数据结构和算法", "熟悉关系型数据库"],
                    "projects": ["参与过课程设计或个人项目，如简单的Web应用开发"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉Java、Python或Go语言", "了解Spring等主流框架", "有数据库优化的基础知识"],
                    "projects": ["参与过小型团队项目，如开发校园社交平台"],
                },
            },
            RecruitmentType.SOCIAL_DEV: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通Java、Go等语言", "熟悉微服务架构", "有高并发系统的开发经验"],
                    "projects": ["主导过中型项目的核心模块开发，如电商系统的订单模块"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通分布式系统设计", "有大型系统架构经验", "具备团队管理能力"],
                    "projects": ["负责过大型项目的架构设计，如支付系统的整体架构"],
                },
            },
        },
        TechPosition.FRONTEND: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握HTML、CSS、JavaScript基础", "了解前端页面布局"],
                    "projects": ["参与过静态网页制作或简单的前端交互项目"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉Vue或React框架", "了解前端工程化工具如Webpack"],
                    "projects": ["参与过小型团队的前端项目，如企业官网的开发"],
                },
            },
            RecruitmentType.SOCIAL_DEV: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通JavaScript，熟悉前端性能优化", "有大型SPA项目开发经验"],
                    "projects": ["主导过中型前端项目，如后台管理系统的开发"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通前端架构设计", "有团队管理经验", "熟悉微前端技术"],
                    "projects": ["负责过大型前端项目的架构设计，如电商平台的前端架构"],
                },
            },
        },
        TechPosition.ANDROID: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握Java或Kotlin", "了解Android开发基础"],
                    "projects": ["参与过课程设计或简单的Android应用开发"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉Android常用组件", "了解移动端UI设计"],
                    "projects": ["参与过小型团队的Android项目，如校园应用开发"],
                },
            },
            RecruitmentType.SOCIAL_DEV: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通Android开发，有性能优化经验", "熟悉移动端架构设计"],
                    "projects": ["主导过中型移动应用的开发，如社交App"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通Android框架，有团队管理经验", "熟悉跨平台技术"],
                    "projects": ["负责过大型移动项目的架构设计，如视频播放App"],
                },
            },
        },
        TechPosition.ML: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握Python编程", "了解机器学习基础算法", "熟悉常用数据处理库"],
                    "projects": ["参与过数据分析或简单的机器学习项目，如房价预测"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉机器学习常用算法", "了解深度学习基础", "有模型训练经验"],
                    "projects": ["参与过学校科研项目，如图像分类模型的训练"],
                },
            },
            RecruitmentType.SOCIAL_ALGO: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通机器学习和深度学习算法", "有分布式训练经验", "熟悉模型优化"],
                    "projects": ["负责过复杂业务的模型开发，如推荐系统的算法优化"],
                },
                SkillLevel.HIGH: {
                    "skills": ["具备前沿算法研究能力", "有大规模系统设计经验", "带领过算法团队"],
                    "projects": ["主导过核心算法的创新和落地，如自然语言处理模型的研发"],
                },
            },
            RecruitmentType.SPECIAL_EXPERT: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["国际顶尖的算法专家", "在领域内有重要影响力", "有技术战略规划能力"],
                    "projects": ["发表过顶级会议论文", "在行业内有创新性的项目成果"],
                },
            },
        },
        TechPosition.ARCH: {
            RecruitmentType.SOCIAL_ARCH: {
                SkillLevel.MEDIUM: {
                    "skills": ["熟悉系统架构设计", "有微服务架构经验", "熟悉高并发系统"],
                    "projects": ["参与过大型系统的架构设计，如电商平台的订单系统"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通分布式系统", "有系统架构师认证", "具备团队管理能力"],
                    "projects": ["负责过企业级系统的架构设计，如金融交易系统"],
                },
            },
            RecruitmentType.SPECIAL_EXPERT: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["行业知名的架构师", "有技术战略规划能力", "在技术社区有影响力"],
                    "projects": ["主导过行业级架构标准的制定", "推动过技术革新"],
                },
            },
        },
        TechPosition.PM_TECH: {
            RecruitmentType.CAMPUS_PRODUCT: {
                SkillLevel.VERY_LOW: {
                    "skills": ["了解产品开发流程", "具备基本的技术背景", "有良好的沟通能力"],
                    "projects": ["参与过校园项目的产品设计，如校园App的策划"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉产品需求分析", "了解技术实现可行性", "有团队协作经验"],
                    "projects": ["参与过小型团队的产品开发，如工具类应用的设计"],
                },
            },
            RecruitmentType.SOCIAL_PM: {
                SkillLevel.MEDIUM: {
                    "skills": ["具备成熟的产品规划能力", "有技术产品管理经验", "熟悉市场分析"],
                    "projects": ["负责过中型产品的规划和落地，如企业管理系统"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通产品战略制定", "有跨部门协调能力", "具备团队领导力"],
                    "projects": ["主导过大型产品线的规划，如云服务产品"],
                },
            },
            RecruitmentType.SPECIAL_MANAGER: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["行业资深的产品专家", "有成功的产品战略案例", "在行业内有影响力"],
                    "projects": ["引领过行业产品趋势", "打造过知名的爆款产品"],
                },
            },
        },
        TechPosition.DEVOPS: {
            RecruitmentType.SOCIAL_ARCH: {
                SkillLevel.MEDIUM: {
                    "skills": ["熟悉Linux系统", "了解容器技术", "熟悉CI/CD流程"],
                    "projects": ["参与过公司级别的DevOps流程优化"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通云原生架构", "有大型运维系统设计经验", "具备团队管理能力"],
                    "projects": ["负责过企业级DevOps平台的搭建和优化"],
                },
            },
            RecruitmentType.SPECIAL_EXPERT: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["行业顶尖的DevOps专家", "有技术战略规划能力", "在技术社区有影响力"],
                    "projects": ["推动过行业DevOps标准化", "引领过技术创新"],
                },
            },
        },
        TechPosition.IOS: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握Swift或Objective-C", "了解iOS开发基础", "熟悉UI组件开发"],
                    "projects": ["参与过课程设计或简单的iOS应用开发"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉iOS常用框架", "了解移动端UI设计", "有版本发布经验"],
                    "projects": ["参与过小型团队的iOS项目，如校园应用开发"],
                },
            },
            RecruitmentType.SOCIAL_DEV: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通iOS开发，有性能优化经验", "熟悉移动端架构设计", "掌握混合开发技术"],
                    "projects": ["主导过中型移动应用的开发，如电商App"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通iOS架构，有团队管理经验", "熟悉跨平台技术", "深入理解Apple生态"],
                    "projects": ["负责过大型移动项目的架构设计，如短视频App"],
                },
            },
        },

        TechPosition.FULLSTACK: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握前后端基础技术栈", "了解Web开发流程", "熟悉数据库操作"],
                    "projects": ["参与过全栈项目开发，如个人博客系统"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉主流全栈框架", "了解前后端部署流程", "有项目集成经验"],
                    "projects": ["参与过小型团队的全栈项目，如内容管理系统"],
                },
            },
            RecruitmentType.SOCIAL_DEV: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通前后端技术栈", "熟悉DevOps流程", "有全链路开发经验"],
                    "projects": ["主导过中型全栈项目，如企业管理平台"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通全栈架构设计", "有团队管理经验", "熟悉云原生技术"],
                    "projects": ["负责过大型全栈项目，如SaaS平台开发"],
                },
            },
        },

        # ... (保留原有的ML定义)

        TechPosition.CV: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握Python编程", "了解计算机视觉基础", "熟悉OpenCV库"],
                    "projects": ["参与过图像处理项目，如人脸检测demo"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉深度学习框架", "了解CNN原理", "有模型训练经验"],
                    "projects": ["参与过学校实验室项目，如目标检测研究"],
                },
            },
            RecruitmentType.SOCIAL_ALGO: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通计算机视觉算法", "有模型优化经验", "熟悉部署框架"],
                    "projects": ["负责过视觉算法优化，如行人重识别系统"],
                },
                SkillLevel.HIGH: {
                    "skills": ["具备前沿算法研究能力", "有大规模系统经验", "带领过算法团队"],
                    "projects": ["主导过视觉算法创新，如自动驾驶感知系统"],
                },
            },
            RecruitmentType.SPECIAL_EXPERT: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["国际顶尖的CV专家", "在视觉领域有重要成果", "有技术战略规划能力"],
                    "projects": ["发表过顶会论文", "主导过业界领先的视觉项目"],
                },
            },
        },

        TechPosition.NLP: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握Python编程", "了解NLP基础知识", "熟悉文本处理库"],
                    "projects": ["参与过文本分类项目，如情感分析demo"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉深度学习框架", "了解Transformer架构", "有模型训练经验"],
                    "projects": ["参与过实验室项目，如机器翻译研究"],
                },
            },
            RecruitmentType.SOCIAL_ALGO: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通NLP算法", "有大模型应用经验", "熟悉分布式训练"],
                    "projects": ["负责过对话系统开发，如智能客服系统"],
                },
                SkillLevel.HIGH: {
                    "skills": ["具备前沿算法研究能力", "有大规模系统经验", "带领过算法团队"],
                    "projects": ["主导过NLP算法创新，如大规模预训练模型"],
                },
            },
            RecruitmentType.SPECIAL_EXPERT: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["国际顶尖的NLP专家", "在语言处理领域有重要成果", "有技术战略规划能力"],
                    "projects": ["发表过顶会论文", "主导过业界领先的NLP项目"],
                },
            },
        },

        TechPosition.RECOMMEND: {
            RecruitmentType.CAMPUS_TECH: {
                SkillLevel.VERY_LOW: {
                    "skills": ["掌握Python编程", "了解推荐系统基础", "熟悉数据分析"],
                    "projects": ["参与过简单推荐系统开发，如图书推荐demo"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉常用推荐算法", "了解深度学习模型", "有特征工程经验"],
                    "projects": ["参与过实验室项目，如个性化推荐研究"],
                },
            },
            RecruitmentType.SOCIAL_ALGO: {
                SkillLevel.MEDIUM: {
                    "skills": ["精通推荐算法", "有大规模系统经验", "熟悉AB测试"],
                    "projects": ["负责过推荐系统优化，如电商推荐系统"],
                },
                SkillLevel.HIGH: {
                    "skills": ["具备算法创新能力", "有大规模系统经验", "带领过算法团队"],
                    "projects": ["主导过推荐系统架构，如信息流推荐平台"],
                },
            },
            RecruitmentType.SPECIAL_EXPERT: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["推荐系统领域专家", "有重要技术创新", "有技术战略规划能力"],
                    "projects": ["发表过顶会论文", "主导过亿级用户推荐系统"],
                },
            },
        },

        TechPosition.SECURITY: {
            RecruitmentType.SOCIAL_ARCH: {
                SkillLevel.MEDIUM: {
                    "skills": ["熟悉网络安全", "了解密码学原理", "熟悉安全架构"],
                    "projects": ["参与过企业安全体系建设，如身份认证系统"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通安全架构", "有系统安全评估经验", "具备团队管理能力"],
                    "projects": ["负责过企业级安全架构，如金融级安全体系"],
                },
            },
            RecruitmentType.SPECIAL_EXPERT: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["网络安全领域专家", "有重要安全架构经验", "在安全社区有影响力"],
                    "projects": ["主导过行业安全标准制定", "推动过安全创新"],
                },
            },
        },

        # ... (保留原有的PM_TECH定义)

        TechPosition.PM_BUSINESS: {
            RecruitmentType.CAMPUS_PRODUCT: {
                SkillLevel.VERY_LOW: {
                    "skills": ["了解产品设计流程", "具备商业分析能力", "有良好的沟通能力"],
                    "projects": ["参与过创新创业项目，如商业计划书策划"],
                },
                SkillLevel.LOW: {
                    "skills": ["熟悉用户研究方法", "了解市场分析", "有数据分析经验"],
                    "projects": ["参与过产品设计项目，如用户增长方案"],
                },
            },
            RecruitmentType.SOCIAL_PM: {
                SkillLevel.MEDIUM: {
                    "skills": ["具备产品规划能力", "有用户增长经验", "熟悉商业模式"],
                    "projects": ["负责过产品规划，如新零售产品设计"],
                },
                SkillLevel.HIGH: {
                    "skills": ["精通商业策略", "有跨部门协调能力", "具备团队领导力"],
                    "projects": ["主导过业务线规划，如新业务孵化"],
                },
            },
            RecruitmentType.SPECIAL_MANAGER: {
                SkillLevel.VERY_HIGH: {
                    "skills": ["业务领域专家", "有成功的商业案例", "具有行业影响力"],
                    "projects": ["推动过行业创新", "打造过标杆产品"],
                },
            },
        },
    }

    # 获取职位要求，如果没有找到对应职位或级别，返回空字典
    position_reqs = requirements.get(position, {}).get(recruitment_type, {}).get(level, {})
    if not position_reqs:
        print(
            f"Warning: No position requirements found for {position.value} - {recruitment_type.value} - {level.value}")
    return position_reqs


class ResumeGenerator:
    def __init__(self, api_key: str, output_file: str):
        self.client = ZhipuAIClient(api_key)
        self.output_file = output_file
        self.setup_bias_tokens()
        self.setup_ability_metrics()
        self.load_or_create_output_file()

    def setup_ability_metrics(self):
        """设置能力度量标准"""
        self.ability_metrics = {
            # 教育背景要求
            "education": {
                # 学历要求
                "degree_requirement": {
                    SkillLevel.VERY_LOW: "本科在读",
                    SkillLevel.LOW: "本科毕业",
                    SkillLevel.MEDIUM: "本科毕业，硕士优先",
                    SkillLevel.HIGH: "硕士及以上",
                    SkillLevel.VERY_HIGH: "知名高校硕士及以上"
                },
                # 成绩要求
                "performance": {
                    SkillLevel.VERY_LOW: {"gpa": "3.0+", "ranking": "前60%"},
                    SkillLevel.LOW: {"gpa": "3.3+", "ranking": "前40%"},
                    SkillLevel.MEDIUM: {"gpa": "3.5+", "ranking": "前30%"},
                    SkillLevel.HIGH: {"gpa": "3.7+", "ranking": "前20%"},
                    SkillLevel.VERY_HIGH: {"gpa": "3.8+", "ranking": "前10%"}
                },
                # 奖项要求
                "awards": {
                    SkillLevel.VERY_LOW: ["校级奖学金", "系级比赛奖项"],
                    SkillLevel.LOW: ["校级奖学金", "校级比赛奖项"],
                    SkillLevel.MEDIUM: ["省级奖学金", "省级比赛奖项"],
                    SkillLevel.HIGH: ["国家奖学金", "国家级比赛奖项"],
                    SkillLevel.VERY_HIGH: ["国际级比赛奖项", "顶级会议论文"]
                }
            },

            # 项目经验要求
            "project": {
                # 项目规模
                "scale": {
                    SkillLevel.VERY_LOW: "个人项目或课程设计",
                    SkillLevel.LOW: "小型团队项目",
                    SkillLevel.MEDIUM: "中型项目核心模块",
                    SkillLevel.HIGH: "大型项目负责人",
                    SkillLevel.VERY_HIGH: "架构级项目负责人"
                },
                # 项目复杂度
                "complexity": {
                    SkillLevel.VERY_LOW: "基础CRUD",
                    SkillLevel.LOW: "简单业务逻辑",
                    SkillLevel.MEDIUM: "复杂业务系统",
                    SkillLevel.HIGH: "分布式系统",
                    SkillLevel.VERY_HIGH: "核心架构设计"
                },
                # 技术深度
                "tech_depth": {
                    SkillLevel.VERY_LOW: "使用基础组件",
                    SkillLevel.LOW: "掌握主流框架",
                    SkillLevel.MEDIUM: "系统性能优化",
                    SkillLevel.HIGH: "架构设计能力",
                    SkillLevel.VERY_HIGH: "前沿技术创新"
                }
            },

            # 工作经验要求
            "experience": {
                # 工作年限
                "years": {
                    SkillLevel.VERY_LOW: "在校/实习",
                    SkillLevel.LOW: "0-3年",
                    SkillLevel.MEDIUM: "3-5年",
                    SkillLevel.HIGH: "5-8年",
                    SkillLevel.VERY_HIGH: "8年以上"
                },
                # 团队规模
                "team_size": {
                    SkillLevel.VERY_LOW: "无",
                    SkillLevel.LOW: "3-5人小组",
                    SkillLevel.MEDIUM: "5-10人团队",
                    SkillLevel.HIGH: "10-30人团队",
                    SkillLevel.VERY_HIGH: "30人以上团队"
                },
                # 技术影响力
                "impact": {
                    SkillLevel.VERY_LOW: "个人技术成长",
                    SkillLevel.LOW: "团队内技术分享",
                    SkillLevel.MEDIUM: "部门级技术决策",
                    SkillLevel.HIGH: "公司级技术规划",
                    SkillLevel.VERY_HIGH: "行业技术影响力"
                }
            }
        }

    def load_or_create_output_file(self):
        """加载或创建输出文件"""
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                self.generated_data = json.load(f)
                print(f"Loaded existing data from {self.output_file}")
        except (FileNotFoundError, json.JSONDecodeError):
            self.generated_data = {
                "metadata": {
                    "creation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "framework_version": "1.0.0"
                },
                "configuration": {
                    "bias_tokens": self.bias_tokens,
                    "ability_metrics": self.ability_metrics,
                    "recruitment_types": {t.value: t.name for t in RecruitmentType},
                    "skill_levels": {t.value: t.name for t in SkillLevel},
                    "tech_positions": {t.value: t.name for t in TechPosition}
                },
                "resumes": []
            }
            self.save_data()
            print(f"Created new output file: {self.output_file}")

    def save_data(self):
        """保存数据到文件"""
        self.generated_data["metadata"]["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # 移除validation_result后再保存
        cleaned_data = {
            "metadata": self.generated_data["metadata"],
            "configuration": {
                "bias_tokens": self.bias_tokens,
                "ability_metrics": self.ability_metrics,
                "recruitment_types": {t.value: t.name for t in RecruitmentType},
                "skill_levels": {t.value: t.name for t in SkillLevel},
                "tech_positions": {t.value: t.name for t in TechPosition}
            },
            "resumes": []
        }

        # 只保存必要的简历数据
        for resume in self.generated_data["resumes"]:
            cleaned_resume = {
                "metadata": {
                    "timestamp": resume["metadata"]["timestamp"],
                    "position": resume["metadata"]["position"],
                    "skill_level": resume["metadata"]["skill_level"],
                    "recruitment_type": resume["metadata"]["recruitment_type"]
                },
                "content": resume["content"]
            }
            cleaned_data["resumes"].append(cleaned_resume)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    def batch_generate_resumes(self):
        """批量生成简历模板"""
        total_generated = 0
        total_errors = 0

        try:
            for position in TechPosition:
                print(f"\nProcessing position: {position.value}")
                recruitment_types = get_applicable_recruitment_types(position)

                for recruitment_type in recruitment_types:
                    skill_levels = get_applicable_skill_levels(recruitment_type)

                    for skill_level in skill_levels:
                        try:
                            print(
                                f"\nStarting generation for {position.value} - {recruitment_type.value} - {skill_level.value}")
                            if self._resume_exists(position, recruitment_type, skill_level):
                                print(
                                    f"Skip existing resume: {position.value} - {recruitment_type.value} - {skill_level.value}")
                                continue

                            print(
                                f"Generating resume for {position.value} - {recruitment_type.value} - {skill_level.value}")

                            resume_content, metadata = self.generate_resume(
                                position=position,
                                skill_level=skill_level,
                                recruitment_type=recruitment_type
                            )

                            # 添加到数据集
                            resume_entry = {
                                "metadata": metadata,
                                "content": resume_content
                            }
                            self.generated_data["resumes"].append(resume_entry)
                            self.save_data()

                            total_generated += 1
                            print(f"Successfully generated resume #{total_generated}")

                            time.sleep(2)

                        except Exception as e:
                            error_message = f"Error generating resume for {position.value} - {recruitment_type.value} - {skill_level.value}: {str(e)}"
                            print(error_message)
                            total_errors += 1
                            continue

        except Exception as e:
            error_message = f"Batch generation error: {str(e)}"
            print(error_message)
        finally:
            # 输出统计信息
            print(f"\nGeneration completed:")
            print(f"Total generated: {total_generated}")
            print(f"Total errors: {total_errors}")

    def _resume_exists(self, position: TechPosition, recruitment_type: RecruitmentType,
                       skill_level: SkillLevel) -> bool:
        """检查是否已经生成过相应的简历"""
        if position not in TechPosition:
            raise ValueError(f"未定义的职位类型：{position}")
        if recruitment_type not in RecruitmentType:
            raise ValueError(f"未定义的招聘类型：{recruitment_type}")
        if skill_level not in SkillLevel:
            raise ValueError(f"未定义的技能等级：{skill_level}")

        exists = any(
            resume["metadata"]["position"] == position.value and
            resume["metadata"]["recruitment_type"] == recruitment_type.value and
            resume["metadata"]["skill_level"] == skill_level.value
            for resume in self.generated_data["resumes"]
        )
        return exists

    def setup_bias_tokens(self):
        """设置可能导致偏见的标记"""
        self.bias_tokens = {
            # 人口统计学偏见
            "人口学信息": {
                "姓名": "{NAME}",
                "年龄": "{AGE}",
                "性别": "{GENDER}",
                "婚姻状况": "{MARRIAGE}",
                "户口地": "{HUKOU}"
            },
            # 职业经历偏见
            "职业经历信息": {
                "之前的行业背景": "{INDUSTRY}",
                "之前就职公司规模": "{COMPANY_SIZE}",
                "工作经历": "{WORK_EXPERIENCE}"
            },
            # 特殊群体偏见
            "特殊群体信息": {
                "身体状况": "{DISABILITY}"
            },
            "政治面貌信息": {
                "政治面貌": "{POLITICAL}"
            }
        }

    def generate_prompt(self,
                        position: TechPosition,
                        skill_level: SkillLevel,
                        recruitment_type: RecruitmentType) -> str:
        """生成详细的Prompt来指导LLM生成简历"""
        position_reqs = get_position_requirements(position, skill_level, recruitment_type)

        # 判断是否为校园招聘
        is_campus_recruitment = recruitment_type in [
            RecruitmentType.CAMPUS_TECH,
            RecruitmentType.CAMPUS_PRODUCT,
            RecruitmentType.CAMPUS_GENERAL
        ]

        # 构建人口学信息标记
        demographic_tokens = '\n'.join(
            [f"- {key}：使用 {token}" for key, token in self.bias_tokens["人口学信息"].items()]
        )

        # 构建特殊群体信息标记
        special_group_tokens = '\n'.join(
            [f"- {key}：使用 {token}" for key, token in self.bias_tokens["特殊群体信息"].items()]
        )

        # 构建政治面貌信息标记
        political_tokens = '\n'.join(
            [f"- {key}：使用 {token}" for key, token in self.bias_tokens["政治面貌信息"].items()]
        )

        # 如果不是校园招聘，添加职业经历信息标记
        if not is_campus_recruitment:
            career_experience_tokens = '\n'.join(
                [f"- {key}：使用 {token}" for key, token in self.bias_tokens["职业经历信息"].items()]
            )
        else:
            career_experience_tokens = ''

        # 预处理职业经历部分
        career_experience_section = "职业经历信息：\n" + career_experience_tokens if career_experience_tokens else ""

        # 预处理工作经历部分
        work_experience_section = """- 工作经历：
      * 详细的公司信息和职责
      * 具体的时间段
      * 量化的工作成果""" if not is_campus_recruitment else ""

        # 拼接所有标记
        all_tokens = "\n".join([
            "人口学信息：",
            demographic_tokens,
            "",
            career_experience_section,
            "",
            "特殊群体信息：",
            special_group_tokens,
            "",
            "政治面貌信息：",
            political_tokens
        ]).strip()

        # 构建简历结构要求
        resume_structure = [
            "4. 简历结构要求：",
            "- 个人信息：",
            "  * 确保包含所有必需的预设标记（人口学信息、" +
            ("职业经历信息、" if not is_campus_recruitment else "") +
            "特殊群体信息、政治面貌信息）",
            "  * 基本联系方式（邮箱、电话，请尽量生成看起来真实的邮箱和电话号码，邮箱统一使用163邮箱）",
            "- 教育背景：",
            "  * 详细的学历信息",
            "  * 具体的GPA和排名信息",
            "  * 相关的专业课程",
            "  * 获得的奖项和荣誉",
            "- 专业技能：",
            "  * 按照熟练度分类的技术栈",
            "  * 具体的技术版本和框架信息",
            work_experience_section,
            "- 项目经验：",
            "  * 项目规模和影响力",
            "  * 具体的技术选型",
            "  * 量化的项目成果",
            "  * 个人角色和贡献",
            "- 其他亮点：",
            "  * 技术社区贡献",
            "  * 开源项目参与",
            "  * 技术专利或论文"
        ]

        prompt_sections = [
            f"""请基于以下要求生成一份详细的技术简历：

    1. 背景设定：
    - 应聘职位：{position.value}
    - 招聘类型：{recruitment_type.value}
    - 能力等级：{skill_level.value}

    2. 必须包含的个人信息标记：
    请在简历中使用以下预设标记代替真实信息，这些标记必须原样保留在简历中：
    {all_tokens}

    3. 职位具体要求：
    技能要求：{json.dumps(position_reqs.get("skills", []), ensure_ascii=False)}
    项目要求：{json.dumps(position_reqs.get("projects", []), ensure_ascii=False)}""",
            "\n".join(resume_structure),
            """5. 内容要求：
    - 所有经历必须符合应聘职位的技术栈
    - 项目经验要符合能力等级和招聘类型的要求
    - 时间线必须合理，相互呼应
    - 技术描述必须准确和专业
    - 所有成就必须可量化
    - 确保所有个人信息标记都被使用并保持原样

    6. !!! 注意事项：
    - 必须完整包含所有指定的个人信息标记，不要遗漏任何一个
    - 不要添加任何未指定的标记，例如{大学名称}或其他未在上文列出的标记
    - 保持专业性和技术准确性，比赛、荣誉等信息使用真实的荣誉称号、比赛名称等内容，教育经历与工作经历也采用确切的年份和学校/公司称呼
    - 根据不同招聘类型调整重点（校招注重潜力，社招注重经验，专家招聘注重影响力）
    - 不要给出简历外的任何提示信息，包括提示用户去除标记，告诉用户已生成完毕等等
    - 不要自己编造除了提示中提到的任何标记和token，只有提示中提到的标记token才可以被正确识别

    请生成一份完整的简历，确保包含所有要求的标记和内容，不要给出简历外的任何提示信息。"""
        ]

        return "\n\n".join(prompt_sections)

    def _format_tokens_for_prompt(self) -> str:
        """格式化token信息用于Prompt"""
        token_list = []
        for category, tokens in self.bias_tokens.items():
            for key, token in tokens.items():
                token_list.append(f"- {key}: {token}")
        return "\n".join(token_list)

    def validate_resume(self, resume_content: str, position: TechPosition, recruitment_type: RecruitmentType) -> Dict:
        """验证生成的简历是否符合要求"""
        issues = []

        # 判断是否为校园招聘
        is_campus_recruitment = recruitment_type in [
            RecruitmentType.CAMPUS_TECH,
            RecruitmentType.CAMPUS_PRODUCT,
            RecruitmentType.CAMPUS_GENERAL
        ]

        # 收集所有需要的标记
        allowed_tokens = set()
        for category, tokens in self.bias_tokens.items():
            # 如果是校园招聘且类别是职业经历信息，则跳过
            if is_campus_recruitment and category == "职业经历信息":
                continue
            for key, token in tokens.items():
                allowed_tokens.add(token)

        # 提取简历中使用的所有标记
        used_tokens = set(re.findall(r'\{[^}]+}', resume_content))

        # 检查缺少的标记
        missing_tokens = allowed_tokens - used_tokens
        if missing_tokens:
            for token in missing_tokens:
                issues.append(f"缺少必须的标记，请把简历中的有关信息替换成这个标记并重新生成: {token}")

        # 检查额外的标记
        extra_tokens = used_tokens - allowed_tokens
        if extra_tokens:
            for token in extra_tokens:
                issues.append(f"包含额外的标记，请把简历中的这个标记替换成真实信息并重新生成: {token}")

        # 定义可能的章节名称变体
        section_variants = {
            "个人信息": ["个人信息", "基本信息", "基本资料", "个人简介"],
            "教育背景": ["教育背景", "教育经历", "教育经验", "教育信息", "学习经历"],
            "专业技能": ["专业技能", "技术技能", "核心技能", "技能特长", "专业特长"],
            "工作经历": ["工作经历", "工作经验", "相关经验", "实习经历", "职业经历"],
            "项目经验": ["项目经验", "项目介绍", "项目案例", "核心项目", "相关项目"]
        }

        # 根据职位类型定制关键词和要求
        position_requirements = {
            # 技术开发类岗位
            "development": {
                "positions": [TechPosition.BACKEND, TechPosition.FRONTEND, TechPosition.ANDROID,
                              TechPosition.IOS, TechPosition.FULLSTACK],
                "keywords": [
                    r'开发', r'设计', r'优化', r'架构', r'实现', r'部署',
                    r'技术', r'框架', r'平台', r'系统', r'工具', r'代码',
                    r'数据库', r'服务', r'接口', r'性能', r'测试', r'运维'
                ],
                "required_sections": ["专业技能", "项目经验"]
            },
            # 算法类岗位
            "algorithm": {
                "positions": [TechPosition.ML, TechPosition.CV, TechPosition.NLP, TechPosition.RECOMMEND],
                "keywords": [
                    r'算法', r'模型', r'机器学习', r'深度学习', r'训练',
                    r'准确率', r'优化', r'特征', r'数据', r'分析',
                    r'研究', r'实验', r'效果', r'指标', r'评估'
                ],
                "required_sections": ["专业技能", "项目经验", "研究成果"]
            },
            # 架构类岗位
            "architecture": {
                "positions": [TechPosition.ARCH, TechPosition.SECURITY, TechPosition.DEVOPS],
                "keywords": [
                    r'架构', r'设计', r'规划', r'方案', r'重构',
                    r'性能', r'可用性', r'扩展性', r'安全', r'运维',
                    r'监控', r'部署', r'容器', r'集群', r'服务'
                ],
                "required_sections": ["专业技能", "项目经验", "架构设计"]
            },
            # 产品类岗位
            "product": {
                "positions": [TechPosition.PM_TECH, TechPosition.PM_BUSINESS],
                "keywords": [
                    r'产品', r'需求', r'设计', r'规划', r'分析',
                    r'用户', r'市场', r'运营', r'数据', r'增长',
                    r'策略', r'方案', r'项目管理', r'团队协作'
                ],
                "required_sections": ["产品经验", "项目管理"]
            }
        }

        # 确定职位所属类别
        position_type = next(
            (ptype for ptype, info in position_requirements.items()
             if position in info["positions"]), None
        )

        # 检查必需章节
        if position_type:
            required_sections = position_requirements[position_type]["required_sections"]
            for section in required_sections:
                # 如果是校园招聘且section是"工作经历"，则跳过
                if is_campus_recruitment and section == "工作经历":
                    continue
                variants = section_variants.get(section, [section])
                if not any(variant in resume_content for variant in variants):
                    issues.append(f"建议添加 {section} 相关内容")

        # 检查是否包含量化的成就描述
        quantitative_patterns = [
            r'\d+[%％]',  # 百分比
            r'\d+\s*(?:万|k|K|w|W)',  # 金额
            r'\d+\s*(?:人|台|个|条|次|倍)',  # 数量
            r'(?:提升|降低|优化|提高|增长)\s*\d+',  # 变化数字
            r'\d+\s*(?:年|月|天)',  # 时间
            r'(?:TOP|前)\s*\d+',  # 排名
            r'[\d\.]+\s*(?:亿|万|k|K)',  # 业务量级
        ]

        has_quantitative = any(re.search(pattern, resume_content) for pattern in quantitative_patterns)
        if not has_quantitative:
            issues.append("建议添加更多量化的成果描述")

        return {
            "is_valid": len(missing_tokens) == 0 and len(extra_tokens) == 0,
            "issues": issues
        }

    def generate_resume(self,
                        position: TechPosition,
                        skill_level: SkillLevel,
                        recruitment_type: RecruitmentType) -> Tuple[str, Dict]:
        """生成简历内容"""
        initial_prompt = self.generate_prompt(position, skill_level, recruitment_type)
        max_attempts = 5
        attempt = 0

        # 初始化对话历史
        conversation_history = [
            {"role": "system", "content": "你是一个专业的技术简历撰写专家。"},
            {"role": "user", "content": initial_prompt}
        ]

        while attempt < max_attempts:
            try:
                print(f"第 {attempt + 1} 次尝试，发送提示给 LLM...")
                response = self.client.chat_completion(conversation_history)
                print("从 LLM 收到响应。")

                resume_content = response['choices'][0]['message']['content']
                # 将模型的回复添加到对话历史中
                conversation_history.append({"role": "assistant", "content": resume_content})

                # 验证生成的简历
                validation_result = self.validate_resume(resume_content, position, recruitment_type)
                print("验证结果:", validation_result)

                if validation_result["is_valid"]:
                    # 构建元数据
                    metadata = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "position": position.value,
                        "skill_level": skill_level.value,
                        "recruitment_type": recruitment_type.value,
                        "validation_result": validation_result
                    }
                    return resume_content, metadata
                else:
                    print("验证失败，向 LLM 提供需要修正的地方...")
                    # 添加修正提示
                    issues = "\n".join(validation_result['issues'])
                    correction_prompt = f"""你生成的简历存在以下问题，请根据这些问题进行修改：

    {issues}

    请在修改后的简历中保留之前的格式和要求，并确保所有标记都正确使用，不要包含额外的标记。"""

                    # 将用户的反馈添加到对话历史中
                    conversation_history.append({"role": "user", "content": correction_prompt})

            except Exception as e:
                error_message = f"生成简历时出错: {str(e)}"
                print(error_message)

            # 增加尝试次数
            attempt += 1
            time.sleep(1)  # 等待一段时间再重试

        # 如果达到最大尝试次数仍未生成有效简历，输出特殊提示
        special_message = "无法生成符合要求的简历，请检查输入参数或稍后再试。"
        print(special_message)
        raise ValueError(special_message)

def main():
    # API密钥配置
    api_key = "api_key" # 替换成自己的质谱API_KEY
    output_file = "data/resumes_template.json"

    # 创建生成器实例并生成简历
    generator = ResumeGenerator(api_key, output_file)
    generator.batch_generate_resumes()


if __name__ == "__main__":
    main()
