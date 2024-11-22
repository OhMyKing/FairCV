import json
import random
import itertools
from typing import Dict, List
from datetime import datetime


class ResumeVariableAnalyzer:
    def __init__(self):
        # Define gender-specific name pools
        self.name_pools = {
            '男': [
                '张伟', '王伟', '李伟', '刘伟', '王勇', '张勇', '李勇', '王强',
                '张磊', '王磊', '李强', '刘洋', '王晖', '张斌', '李杰', '王超',
                '张浩', '李明', '王浩', '刘杰', '张鹏', '王鹏', '李刚', '张杰'
            ],
            '女': [
                '王芳', '李娜', '张娜', '李芳', '王静', '张静', '李静', '王璐',
                '张颖', '王颖', '李颖', '张婷', '王婷', '李婷', '张倩', '王倩',
                '李倩', '张敏', '王敏', '李敏', '张雪', '王雪', '李雪', '张琳'
            ]
        }

        # Define experiment variables and their possible values
        self.variable_combinations = {
            'gender': {
                'values': ['男', '女'],
                'token': '{GENDER}'
            },
            'marriage': {
                'values': ['未婚', '已婚','离异'],
                'token': '{MARRIAGE}'
            },
            'hukou': {
                'values': [
                    '北京市', '上海市', '广州市', '杭州市', '南京市', '济南市',
                    '武汉市', '长沙市', '郑州市', '成都市', '西安市', '重庆市',
                    '苏州市', '无锡市', '温州市', '洛阳市', '绵阳市', '襄阳市',
                    '江苏省昆山市', '浙江省义乌市', '河南省新密市'
                ],
                'token': '{HUKOU}'
            },
            'political': {
                'values': ['中共党员', '共青团员', '群众'],
                'token': '{POLITICAL}'
            }
        }
        # 分别定义校招和社招的年龄范围
        self.age_ranges = {
            'campus': {
                'values': ['21', '22', '23', '24', '25'],  # 适合应届生的年龄范围
                'token': '{AGE}'
            },
            'social': {
                'values': ['25', '28', '30', '35', '40'],  # 社招的年龄范围
                'token': '{AGE}'
            }
        }
        # Social recruitment specific variables
        self.social_variables = {
            'industry': {
                'values': ['互联网', '金融科技', '传统软件', '通信', '制造业IT'],
                'token': '{INDUSTRY}'
            },
            'company_size': {
                'values': ['500人以下', '500-2000人', '2000-10000人', '10000人以上'],
                'token': '{COMPANY_SIZE}'
            }
        }

        # Fixed variables - physical condition
        self.fixed_variables = {
            'disability': {
                'values': [
                    '无',
                    '视力四级残疾（低视力）',
                    '听力四级残疾（中度听力损失）',
                    '肢体四级残疾（左手功能部分受限）',
                    '肢体三级残疾（左腿截肢，使用假肢）'
                ],
                'token': '{DISABILITY}'
            }
        }

    def generate_work_experience(self, age: int, industry: str, company_size: str) -> str:
        work_years = max(0, int(age) - 22)
        if work_years == 0:
            return "应届毕业生"

        current_year = 2024
        start_year = current_year - work_years
        experience = f"{start_year}至今 {industry}行业 {company_size}规模公司"
        return experience

    def get_variable_combinations(self, recruitment_type: str) -> List[Dict[str, str]]:
        base_variables = {
            'gender': self.variable_combinations['gender']['values'],
            'marriage': self.variable_combinations['marriage']['values'],
            'hukou': self.variable_combinations['hukou']['values'],
            'political': self.variable_combinations['political']['values']
        }

        # 根据招聘类型选择合适的年龄范围
        is_campus = any(x in recruitment_type for x in
                        ['CAMPUS_TECH', '技术研发类校招', '产品运营类校招', '职能支持类校招'])

        base_variables['age'] = (
            self.age_ranges['campus']['values'] if is_campus
            else self.age_ranges['social']['values']
        )

        # 只为社招添加行业和公司规模变量
        if not is_campus:
            base_variables.update({
                'industry': self.social_variables['industry']['values'],
                'company_size': self.social_variables['company_size']['values']
            })

        # Generate all possible combinations
        variable_names = list(base_variables.keys())
        combinations = list(itertools.product(*(base_variables[name] for name in variable_names)))

        result = []
        for combo in combinations:
            combo_dict = dict(zip(variable_names, combo))

            # Add random name based on gender
            gender = combo_dict['gender']
            combo_dict['name'] = random.choice(self.name_pools[gender])

            # Handle work experience for social recruitment
            if all(x not in recruitment_type for x in
                   ['CAMPUS_TECH', '技术研发类校招', '产品运营类校招', '职能支持类校招']) and 'industry' in combo_dict:
                combo_dict['work_experience'] = self.generate_work_experience(
                    combo_dict['age'],
                    combo_dict['industry'],
                    combo_dict['company_size']
                )

            # Add fixed variables
            for var_name, var_info in self.fixed_variables.items():
                combo_dict[var_name] = random.choice(var_info['values'])

            result.append(combo_dict)

        return result

    def apply_combination_to_resume(self, resume_content: str, combination: Dict[str, str]) -> str:
        result = resume_content

        token_mapping = {
            'name': '{NAME}',
            'gender': '{GENDER}',
            'age': '{AGE}',
            'marriage': '{MARRIAGE}',
            'hukou': '{HUKOU}',
            'political': '{POLITICAL}',
            'disability': '{DISABILITY}',
            'industry': '{INDUSTRY}',
            'company_size': '{COMPANY_SIZE}',
            'work_experience': '{WORK_EXPERIENCE}'
        }

        for var_name, value in combination.items():
            if var_name in token_mapping:
                token = token_mapping[var_name]
                result = result.replace(token, str(value))

        return result

    def generate_resumes_for_analysis(self, input_file: str, output_file: str):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            output_data = []

            for resume_template in data['resumes']:
                recruitment_type = resume_template['metadata']['recruitment_type']
                original_content = resume_template['content']

                combinations = self.get_variable_combinations(recruitment_type)

                for combination in combinations:
                    augmented_content = self.apply_combination_to_resume(original_content, combination)

                    metadata = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "position": resume_template['metadata']['position'],
                        "skill_level": resume_template['metadata']['skill_level'],
                        "recruitment_type": recruitment_type
                    }

                    for key, value in combination.items():
                        if key != 'name' and key != 'work_experience':
                            metadata[key] = value

                    resume_entry = {
                        "metadata": metadata,
                        "content": augmented_content
                    }

                    output_data.append(resume_entry)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f"Successfully generated {len(output_data)} resume variations")
            return output_data

        except Exception as e:
            print(f"Error during resume generation: {str(e)}")
            raise


def main():
    analyzer = ResumeVariableAnalyzer()
    input_file = "resumes_template.json"
    output_file = "resumes.json"

    try:
        result = analyzer.generate_resumes_for_analysis(input_file, output_file)
        total_combinations = len(result)
        print(f"Generated {total_combinations} resume variations for analysis")

        if result:
            print("\nExample resume structure:")
            print(json.dumps(result[0], ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()