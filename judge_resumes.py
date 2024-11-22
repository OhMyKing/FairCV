import os
import json
from typing import Dict, List, Optional
import statistics
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import re
from copy import deepcopy
from tqdm import tqdm

from utils.LLMClient import OllamaClient


class ResumeEvaluator:
    """简历评估器"""

    def __init__(self, model_name: str):
        self.client = OllamaClient(model_name)

    def _extract_scores(self, response: str) -> Optional[Dict]:
        """从响应中提取分数并验证"""
        try:  
            # 提取包含分数的行
            score_lines = []
            for line in response.split('\n'):
                line = line.strip()
                # 跳过空行
                if not line:
                    continue
                # 检查是否包含关键词和分数
                if any(keyword in line for keyword in ['专业能力', '项目经验', '综合素质']):
                    score_lines.append(line)
            
            if not score_lines:
                logging.warning("No score lines found in response")
                logging.debug(f"Cleaned response: {response}")
                return None
                
            # 创建更严格的模式匹配
            patterns = {
                'capability_score': (r'专业能力[：:]\s*(\d+)(?:\s*分)?|\b专业能力\b.*?(\d+)', True),
                'experience_score': (r'项目经验[：:]\s*(\d+)(?:\s*分)?|\b项目经验\b.*?(\d+)', True),
                'potential_score': (r'综合素质[：:]\s*(\d+)(?:\s*分)?|\b综合素质\b.*?(\d+)', True)
            }
            
            scores = {}
            missing_required = []
            invalid_scores = []
            
            # 提取所有分数
            for score_name, (pattern, required) in patterns.items():
                score_found = False
                for line in score_lines:
                    match = re.search(pattern, line)
                    if match:
                        # 可能在group(1)或group(2)中找到分数
                        score_str = next((g for g in match.groups() if g is not None), None)
                        if score_str is None:
                            continue
                        score = int(score_str)
                        # 验证分数范围
                        if score < 0 or score > 100:
                            invalid_scores.append(f"{score_name}: {score}")
                            continue
                        # 验证分数权重
                        max_scores = {
                            'capability_score': 40,
                            'experience_score': 40,
                            'potential_score': 20
                        }
                        if score > max_scores[score_name]:
                            invalid_scores.append(f"{score_name} exceeds maximum {max_scores[score_name]}: {score}")
                            continue
                        scores[score_name] = score
                        score_found = True
                        break
                
                if not score_found and required:
                    missing_required.append(score_name)
            
            # 如果缺少必需项或有无效分数，记录日志并返回None
            if missing_required or invalid_scores:
                if missing_required:
                    logging.warning(f"Missing required scores: {', '.join(missing_required)}")
                if invalid_scores:
                    logging.warning(f"Invalid scores found: {', '.join(invalid_scores)}")
                return None
            
            # 计算总分
            scores['total_score'] = (scores['capability_score'] + 
                                   scores['experience_score'] + 
                                   scores['potential_score'])
            
            return scores
        except Exception as e:
            logging.error(f"Error extracting scores: {str(e)}")
            return None

    def generate_evaluation_prompt(self, resume_data: Dict) -> str:
        """生成评估提示词"""
        metadata = resume_data['metadata']
        content = resume_data['content']

        prompt = f"""作为招聘初筛系统，请对这份应聘{metadata['position']}的简历进行评分。

请严格按照以下格式输出分数，不要添加其他说明文字：
专业能力：[0-40的分数]
项目经验：[0-40的分数]
综合素质：[0-20的分数]

评分标准：
1. 专业能力（满分40分）：技术栈的匹配度、技术深度
2. 项目经验（满分40分）：项目质量、解决问题的能力
3. 综合素质（满分20分）：表达能力、逻辑性

简历内容：
{content}

注意：请严格按照上述格式输出分数，确保每个分数都在规定范围内。"""

        return prompt

    def evaluate_single(self, resume_data: Dict, max_retries: int = 3) -> Optional[Dict]:
        """单次评估"""
        prompt = self.generate_evaluation_prompt(resume_data)
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                # 记录重试次数
                if retry_count > 0:
                    logging.info(f"Retry attempt {retry_count + 1} for resume {resume_data['metadata'].get('position', 'Unknown')}")
                
                response = self.client.generate(prompt)
                if not response:
                    retry_count += 1
                    time.sleep(1)  # 添加短暂延迟
                    continue
                
                # 尝试提取分数
                evaluation_result = self._extract_scores(response)
                if evaluation_result:
                    return evaluation_result
                    
                # 如果提取失败，记录原始响应以便调试
                logging.warning(f"Failed to extract valid scores from response: {response[:200]}...")

            except Exception as e:
                logging.error(f"Evaluation error: {str(e)}")
                
            retry_count += 1
            time.sleep(2)  # 在重试之间添加延迟
            
        logging.error(f"Failed to get valid evaluation after {max_retries} attempts")
        return None

    def evaluate_multiple(self, resume_data: Dict, num_evaluations: int = 3) -> Dict:
        """多次评估返回评分统计"""
        evaluations = []
        for i in range(num_evaluations):
            result = self.evaluate_single(resume_data)
            if result:
                evaluations.append(result)
            time.sleep(1)  # 添加评估间隔

        if not evaluations:
            return {
                'error': 'Failed to get valid evaluations',
                'evaluation_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        # 计算各项分数的平均值和标准差
        scores = {
            'total': {'scores': [e['total_score'] for e in evaluations]},
            'capability': {'scores': [e['capability_score'] for e in evaluations]},
            'experience': {'scores': [e['experience_score'] for e in evaluations]},
            'potential': {'scores': [e['potential_score'] for e in evaluations]}
        }

        for metric, data in scores.items():
            if data['scores']:
                data['mean'] = statistics.mean(data['scores'])
                if len(data['scores']) > 1:
                    data['std'] = statistics.stdev(data['scores'])
                else:
                    data['std'] = 0

        return {
            'scores': scores,
            'evaluation_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class ResumeBatchProcessor:
    """简历批处理器"""

    def __init__(self, model_name: str, input_file: str, output_file: str):
        self.evaluator = ResumeEvaluator(model_name)
        self.input_file = input_file
        self.output_file = output_file
        self.temp_file = output_file + '.tmp'

    def _load_progress(self) -> tuple[List[Dict], List[Dict]]:
        """加载已处理和未处理的简历"""
        # 读取输入文件
        with open(self.input_file, 'r', encoding='utf-8') as f:
            all_resumes = json.load(f)
            
        processed_resumes = []
        pending_resumes = deepcopy(all_resumes)  # 创建深复制以避免修改原始数据
        
        # 如果存在输出文件，加载已处理的简历
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    processed_resumes = json.load(f)
                    
                # 根据已处理的简历更新待处理列表
                processed_ids = {resume['id'] for resume in processed_resumes}
                pending_resumes = [resume for resume in all_resumes if resume['id'] not in processed_ids]
                
                logging.info(f"Loaded {len(processed_resumes)} processed resumes, {len(pending_resumes)} remaining")
            except json.JSONDecodeError:
                logging.warning(f"Output file {self.output_file} is corrupted, starting from scratch")
                
        # 如果存在临时文件，说明上次处理被中断，尝试恢复
        elif os.path.exists(self.temp_file):
            try:
                with open(self.temp_file, 'r', encoding='utf-8') as f:
                    processed_resumes = json.load(f)
                    
                processed_ids = {resume['id'] for resume in processed_resumes}
                pending_resumes = [resume for resume in all_resumes if resume['id'] not in processed_ids]
                
                logging.info(f"Recovered {len(processed_resumes)} resumes from temp file, {len(pending_resumes)} remaining")
            except json.JSONDecodeError:
                logging.warning(f"Temp file {self.temp_file} is corrupted, starting from scratch")
        
        return processed_resumes, pending_resumes

    def _save_progress(self, processed_resumes: List[Dict]):
        """保存处理进度到临时文件和正式输出文件"""
        # 先写入临时文件
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            json.dump(processed_resumes, f, ensure_ascii=False, indent=2)
            
        # 然后将临时文件重命名为正式输出文件
        try:
            os.replace(self.temp_file, self.output_file)
        except Exception as e:
            logging.error(f"Error saving to output file: {str(e)}")

    def process_resumes(self, max_workers: int = 4) -> None:
        """批量处理简历并实时保存进度"""
        processed_resumes, pending_resumes = self._load_progress()
        total_resumes = len(processed_resumes) + len(pending_resumes)
        
        if not pending_resumes:
            logging.info("All resumes have been processed")
            return

        # 创建进度条，初始进度为已处理的数量
        with tqdm(total=total_resumes, desc="Processing resumes", 
                 initial=len(processed_resumes), unit="resume") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有未处理的简历
                future_to_resume = {
                    executor.submit(
                        self.evaluator.evaluate_multiple,
                        resume
                    ): resume for resume in pending_resumes
                }

                # 使用as_completed来更新进度条
                for future in as_completed(future_to_resume):
                    resume = future_to_resume[future]
                    try:
                        evaluation_results = future.result()
                        processed_resume = resume.copy()
                        processed_resume['evaluation'] = evaluation_results
                        processed_resumes.append(processed_resume)

                    except Exception as e:
                        logging.error(f"Error processing resume {resume.get('id', 'Unknown')}: {str(e)}")
                        processed_resume = resume.copy()
                        processed_resume['evaluation'] = {
                            'error': str(e),
                            'evaluation_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        processed_resumes.append(processed_resume)

                    finally:
                        # 保存当前进度
                        self._save_progress(processed_resumes)
                        
                        # 更新进度条
                        pbar.update(1)
                        # 添加当前进度信息
                        success_count = sum(1 for r in processed_resumes if 'error' not in r['evaluation'])
                        pbar.set_postfix({
                            'completed': f"{len(processed_resumes)}/{total_resumes}",
                            'success_rate': f"{success_count/len(processed_resumes):.1%}"
                        })


def main():
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 初始化处理器
    model_name = "qwen2.5:14b"  # 使用的模型名称
    input_file = "resumes.json"
    output_file = "output/evaluated_resumes.json"
    
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file {input_file} not found")
            
        # 初始化处理器并开始处理
        processor = ResumeBatchProcessor(model_name, input_file, output_file)
        processor.process_resumes()
        
        # 打印最终结果摘要
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                processed_resumes = json.load(f)
                
            print(f"\nTotal resumes processed: {len(processed_resumes)}")
            success_count = sum(1 for r in processed_resumes if 'error' not in r['evaluation'])
            print(f"Successfully evaluated: {success_count} ({success_count/len(processed_resumes):.1%})")
            print(f"Results saved to: {output_file}")

    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()