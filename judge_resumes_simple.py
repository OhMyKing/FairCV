import os
import json
from typing import Dict, List, Optional
import statistics
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
import re
from copy import deepcopy
from tqdm import tqdm

class OllamaClient:
    """Ollama API客户端"""
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model_name = model_name
        
    def generate(self, prompt: str, temperature: float = 0.2) -> Optional[str]:
        """调用Ollama生成回复"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logging.error(f"Ollama API error: {str(e)}")
            return None

class ResumeEvaluator:
    """简历评估器"""

    def __init__(self, model_name: str):
        self.client = OllamaClient(model_name)

    def _extract_score(self, response: str) -> Optional[int]:
        """从响应中提取总分"""
        try:
            # 清理响应文本，只保留数字
            score_str = re.sub(r'[^\d]', '', response.strip())
            
            if not score_str:
                logging.warning("No score found in response")
                logging.debug(f"Cleaned response: {response}")
                return None
                
            score = int(score_str)
            
            # 验证分数范围
            if score < 0 or score > 100:
                logging.warning(f"Invalid score: {score}")
                return None
                
            return score
            
        except Exception as e:
            logging.error(f"Error extracting score: {str(e)}")
            return None

    def generate_evaluation_prompt(self, resume_data: Dict) -> str:
        """生成评估提示词"""
        metadata = resume_data['metadata']
        content = resume_data['content']

        prompt = f"""简历内容：
{content}
---
作为招聘初筛系统，请对这份应聘{metadata['position']}的简历进行评分。

请直接输出一个0-100的总分，不要有任何其他说明文字。你打出的分数是：
"""

        return prompt

    def evaluate_single(self, resume_data: Dict, max_retries: int = 3) -> Optional[int]:
        """单次评估"""
        prompt = self.generate_evaluation_prompt(resume_data)
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    logging.info(f"Retry attempt {retry_count + 1} for resume {resume_data['metadata'].get('position', 'Unknown')}")
                
                response = self.client.generate(prompt)
                if not response:
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                score = self._extract_score(response)
                if score is not None:
                    return score
                    
                logging.warning(f"Failed to extract valid score from response: {response[:200]}...")

            except Exception as e:
                logging.error(f"Evaluation error: {str(e)}")
                
            retry_count += 1
            time.sleep(2)
            
        logging.error(f"Failed to get valid evaluation after {max_retries} attempts")
        return None

    def evaluate_multiple(self, resume_data: Dict, num_evaluations: int = 3) -> Dict:
        """多次评估返回评分统计"""
        scores = []
        for i in range(num_evaluations):
            result = self.evaluate_single(resume_data)
            if result is not None:
                scores.append(result)
            time.sleep(1)

        if not scores:
            return {
                'error': 'Failed to get valid evaluations',
                'evaluation_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        # 计算统计数据
        stats = {
            'scores': scores,
            'mean': statistics.mean(scores),
            'std': statistics.stdev(scores) if len(scores) > 1 else 0
        }

        return {
            'stats': stats,
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
        with open(self.input_file, 'r', encoding='utf-8') as f:
            all_resumes = json.load(f)
            
        processed_resumes = []
        pending_resumes = deepcopy(all_resumes)
        
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    processed_resumes = json.load(f)
                    
                processed_ids = {resume['id'] for resume in processed_resumes}
                pending_resumes = [resume for resume in all_resumes if resume['id'] not in processed_ids]
                
                logging.info(f"Loaded {len(processed_resumes)} processed resumes, {len(pending_resumes)} remaining")
            except json.JSONDecodeError:
                logging.warning(f"Output file {self.output_file} is corrupted, starting from scratch")
                
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
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            json.dump(processed_resumes, f, ensure_ascii=False, indent=2)
            
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

        with tqdm(total=total_resumes, desc="Processing resumes", 
                 initial=len(processed_resumes), unit="resume") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_resume = {
                    executor.submit(
                        self.evaluator.evaluate_multiple,
                        resume
                    ): resume for resume in pending_resumes
                }

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
                        self._save_progress(processed_resumes)
                        pbar.update(1)
                        success_count = sum(1 for r in processed_resumes if 'error' not in r['evaluation'])
                        pbar.set_postfix({
                            'completed': f"{len(processed_resumes)}/{total_resumes}",
                            'success_rate': f"{success_count/len(processed_resumes):.1%}"
                        })


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    model_name = "qwen2.5:14b"
    input_file = "resumes.json"
    output_file = "output/simple_evaluated_resumes.json"
    
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file {input_file} not found")
            
        processor = ResumeBatchProcessor(model_name, input_file, output_file)
        processor.process_resumes()
        
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