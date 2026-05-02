"""
AI-Orchestra: 调度中心 (Orchestrator)
负责协调多个AI之间的协作流程
"""

import asyncio
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from base_agent import BaseAgent, MockAgent, PersonalityType, create_agent


class HierarchyMode:
    """
    三级决策模式：学生 -> 老师 -> 校长
    """
    
    def __init__(self, students: List[BaseAgent], teachers: List[BaseAgent], 
                 principal: BaseAgent):
        self.students = students
        self.teachers = teachers
        self.principal = principal
        self.results = {
            "students": {},
            "teachers": {},
            "principal": "",
            "timeline": []
        }
    
    async def execute(self, question: str, progress_callback=None) -> Dict[str, Any]:
        """
        执行三级决策流程
        
        Args:
            question: 用户问题
            progress_callback: 进度回调函数 (stage, message, data)
        
        Returns:
            完整结果字典
        """
        self.results["question"] = question
        self.results["start_time"] = datetime.now().isoformat()
        
        # Stage 1: 学生组同时回答
        if progress_callback:
            progress_callback("stage1", "学生组正在思考...", {"total": len(self.students)})
        
        student_tasks = [
            self._student_answer(agent, question) 
            for agent in self.students
        ]
        student_results = await asyncio.gather(*student_tasks)
        
        for i, (agent, answer) in enumerate(zip(self.students, student_results)):
            self.results["students"][agent.name] = {
                "answer": answer,
                "personality": agent.personality.value,
                "order": i + 1
            }
            if progress_callback:
                progress_callback("stage1_progress", f"{agent.name} 已完成", 
                                {"agent": agent.name, "answer": answer[:100]})
        
        # Stage 2: 老师组评判
        if progress_callback:
            progress_callback("stage2", "老师组正在评判...", {"total": len(self.teachers)})
        
        teacher_tasks = [
            self._teacher_evaluate(agent, self.results["students"]) 
            for agent in self.teachers
        ]
        teacher_results = await asyncio.gather(*teacher_tasks)
        
        for i, (agent, evaluation) in enumerate(zip(self.teachers, teacher_results)):
            self.results["teachers"][agent.name] = {
                "evaluation": evaluation,
                "personality": agent.personality.value,
                "order": i + 1
            }
            if progress_callback:
                progress_callback("stage2_progress", f"{agent.name} 已完成评判", 
                                {"agent": agent.name, "evaluation": evaluation[:100]})
        
        # Stage 3: 校长决策
        if progress_callback:
            progress_callback("stage3", "校长正在最终决策...", {})
        
        principal_prompt = self._build_principal_prompt(
            question, 
            self.results["students"], 
            self.results["teachers"]
        )
        principal_answer = await self.principal.generate(principal_prompt)
        
        self.results["principal"] = {
            "answer": principal_answer,
            "personality": self.principal.personality.value,
            "agent_name": self.principal.name
        }
        
        self.results["end_time"] = datetime.now().isoformat()
        
        if progress_callback:
            progress_callback("complete", "决策完成", self.results)
        
        return self.results
    
    async def _student_answer(self, agent: BaseAgent, question: str) -> str:
        """学生回答单个问题"""
        prompt = f"""请回答以下问题，扮演一位{agent.personality.value}风格的学生：

问题：{question}

请给出你的详细分析和见解。"""
        
        return await agent.generate(prompt)
    
    async def _teacher_evaluate(self, agent: BaseAgent, student_answers: Dict) -> str:
        """老师评判所有学生答案"""
        answers_text = "\n\n".join([
            f"【{name}】({data['personality']}): {data['answer'][:300]}..." 
            for name, data in student_answers.items()
        ])
        
        prompt = f"""你是一位资深教师，请以{agent.personality.value}的风格，
对以下6位学生的回答进行专业评判：

{answers_text}

请：
1. 对每个学生的回答打分（0-100分）并说明理由
2. 指出各答案的优点和不足
3. 给出综合性的评价意见"""
        
        return await agent.generate(prompt)
    
    def _build_principal_prompt(self, question: str, student_answers: Dict, 
                                 teacher_evaluations: Dict) -> str:
        """构建给校长的综合决策提示"""
        students_summary = "\n".join([
            f"- {name}({data['personality']}): {data['answer'][:200]}..." 
            for name, data in student_answers.items()
        ])
        
        teachers_summary = "\n".join([
            f"- {name}({data['personality']}): {data['evaluation'][:200]}..." 
            for name, data in teacher_evaluations.items()
        ])
        
        return f"""你是一位经验丰富的校长。基于以下信息，请给出最终结论：

【原始问题】
{question}

【六位学生的回答】
{students_summary}

【三位教师的评判】
{teachers_summary}

请以{self.principal.personality.value}的风格，给出：
1. 最靠谱的简洁结论（100字以内）
2. 结论的置信度（0-100%）
3. 简要说明决策依据"""


class CreativeWritingMode:
    """
    文学创作模式：AI协作创作
    支持网络小说续写、爆款文案生成
    """
    
    WRITING_STYLES = {
        "web_novel": {
            "name": "网络文学",
            "description": "网文风格，爽文/玄幻/言情",
            "agents": ["outline_writer", "plot_writer", "dialogue_writer", "polish_writer"]
        },
        "xiaohongshu": {
            "name": "小红书文案",
            "description": "种草笔记风格，emoji多，口语化",
            "agents": ["hook_writer", "content_writer", "cta_writer"]
        },
        "wechat": {
            "name": "公众号文章",
            "description": "深度长文，有观点有故事",
            "agents": ["title_writer", "intro_writer", "body_writer", "conclusion_writer"]
        },
        "ecommerce": {
            "name": "电商文案",
            "description": "转化率导向，痛点+卖点",
            "agents": ["researcher", "headline_writer", "benefit_writer", "urgency_writer"]
        }
    }
    
    def __init__(self, agents_pool: Dict[str, BaseAgent]):
        self.agents_pool = agents_pool
        self.results = {}
    
    async def create_content(self, content_type: str, topic: str, 
                            requirements: str = "",
                            progress_callback=None) -> Dict[str, Any]:
        """
        创建内容
        
        Args:
            content_type: 内容类型 (web_novel, xiaohongshu, wechat, ecommerce)
            topic: 主题/标题
            requirements: 特殊要求
            progress_callback: 进度回调
        """
        style = self.WRITING_STYLES.get(content_type, self.WRITING_STYLES["wechat"])
        
        self.results = {
            "type": content_type,
            "topic": topic,
            "requirements": requirements,
            "start_time": datetime.now().isoformat(),
            "stages": {}
        }
        
        if content_type == "web_novel":
            return await self._write_novel(topic, requirements, progress_callback)
        elif content_type == "xiaohongshu":
            return await self._write_xiaohongshu(topic, requirements, progress_callback)
        elif content_type == "wechat":
            return await self._write_wechat(topic, requirements, progress_callback)
        elif content_type == "ecommerce":
            return await self._write_ecommerce(topic, requirements, progress_callback)
        
        return self.results
    
    async def _write_novel(self, topic: str, requirements: str, 
                          progress_callback) -> Dict:
        """网络小说创作流程"""
        
        # 阶段1: 大纲规划师
        if progress_callback:
            progress_callback("stage1", "大纲规划师正在构思世界观...", {})
        
        outline_agent = MockAgent("大纲规划师", PersonalityType.ANALYTICAL)
        outline_prompt = f"""你是一位资深网文大纲规划师。
请为以下主题创作详细大纲：

主题：{topic}
要求：{requirements}

请提供：
1. 世界观设定（300字）
2. 主要人物设定（3-5个核心角色）
3. 前10章的剧情大纲（每章100字左右）
4. 爽点设计（3-5个关键爽点）"""
        
        outline = await outline_agent.generate(outline_prompt)
        self.results["stages"]["outline"] = {"agent": "大纲规划师", "content": outline}
        
        if progress_callback:
            progress_callback("stage1_complete", "大纲已完成", {"outline": outline[:200]})
        
        # 阶段2: 情节写手
        if progress_callback:
            progress_callback("stage2", "情节写手正在扩写...", {})
        
        plot_agent = MockAgent("情节写手", PersonalityType.AGGRESSIVE)
        plot_prompt = f"""你是一位擅长写爽文情节的网文作者。
基于以下大纲，请写出第一章的详细内容（2000字）：

大纲：{outline[:500]}...

要求：
- 节奏快，第一章就要有冲突
- 主角要有金手指/特殊能力
- 结尾留悬念"""
        
        plot = await plot_agent.generate(plot_prompt)
        self.results["stages"]["plot"] = {"agent": "情节写手", "content": plot}
        
        if progress_callback:
            progress_callback("stage2_complete", "情节已扩写", {"plot": plot[:200]})
        
        # 阶段3: 对话润色师
        if progress_callback:
            progress_callback("stage3", "对话润色师正在优化...", {})
        
        polish_agent = MockAgent("对话润色师", PersonalityType.HUMOROUS)
        polish_prompt = f"""你是一位擅长写对话的编辑。
请优化以下内容，重点改善：
1. 让人物对话更有性格
2. 增加一些幽默元素
3. 让场景描写更生动

原文：{plot[:1000]}...

请输出润色后的完整第一章。"""
        
        polished = await polish_agent.generate(polish_prompt)
        self.results["stages"]["polished"] = {"agent": "对话润色师", "content": polished}
        
        # 阶段4: 最终审核
        if progress_callback:
            progress_callback("stage4", "主编正在最终审核...", {})
        
        editor_agent = MockAgent("主编", PersonalityType.CAUTIOUS)
        editor_prompt = f"""你是一位资深主编。
请对以下内容进行最终审核，给出：
1. 整体评分（0-100）
2. 优点
3. 需要改进的地方
4. 市场潜力评估

内容：{polished[:800]}..."""
        
        review = await editor_agent.generate(editor_prompt)
        self.results["stages"]["review"] = {"agent": "主编", "content": review}
        
        self.results["final_content"] = polished
        self.results["end_time"] = datetime.now().isoformat()
        
        if progress_callback:
            progress_callback("complete", "创作完成", self.results)
        
        return self.results
    
    async def _write_xiaohongshu(self, topic: str, requirements: str, 
                                  progress_callback) -> Dict:
        """小红书文案创作"""
        
        # 阶段1: 吸睛标题
        if progress_callback:
            progress_callback("stage1", "标题专家正在创作...", {})
        
        title_agent = MockAgent("标题专家", PersonalityType.AGGRESSIVE)
        title_prompt = f"""你是一位小红书爆款标题专家。
请为以下主题创作5个爆款标题：

主题：{topic}
要求：{requirements}

标题要求：
- 有数字（如：3个技巧、5个方法）
- 有情绪词（如：绝了、救命、必看）
- 有悬念或痛点"""
        
        titles = await title_agent.generate(title_prompt)
        self.results["stages"]["titles"] = {"agent": "标题专家", "content": titles}
        
        # 选择第一个标题
        selected_title = titles.split("\n")[0] if "\n" in titles else topic
        
        # 阶段2: 正文创作
        if progress_callback:
            progress_callback("stage2", "内容创作者正在写作...", {})
        
        content_agent = MockAgent("内容创作者", PersonalityType.HUMOROUS)
        content_prompt = f"""你是一位小红书种草达人。
请基于以下标题写一篇种草笔记：

标题：{selected_title}
主题：{topic}

要求：
- 开头要有emoji和吸引人的hook
- 分点叙述，每点配emoji
- 语气亲切像闺蜜聊天
- 结尾要有CTA（点赞收藏关注）
- 适当使用网络流行语"""
        
        content = await content_agent.generate(content_prompt)
        self.results["stages"]["content"] = {"agent": "内容创作者", "content": content}
        
        # 阶段3: 添加标签
        if progress_callback:
            progress_callback("stage3", "标签专家正在添加话题...", {})
        
        tag_agent = MockAgent("标签专家", PersonalityType.ANALYTICAL)
        tag_prompt = f"""请为以下小红书笔记推荐10个热门标签：

内容：{content[:300]}...

格式：#标签1 #标签2 ..."""
        
        tags = await tag_agent.generate(tag_prompt)
        self.results["stages"]["tags"] = {"agent": "标签专家", "content": tags}
        
        # 组装最终内容
        final_content = f"""{selected_title}

{content}

{tags}
"""
        
        self.results["final_content"] = final_content
        self.results["end_time"] = datetime.now().isoformat()
        
        if progress_callback:
            progress_callback("complete", "小红书文案创作完成", self.results)
        
        return self.results
    
    async def _write_wechat(self, topic: str, requirements: str, 
                           progress_callback) -> Dict:
        """公众号文章创作"""
        
        stages = [
            ("标题创作师", "创作10个吸睛标题", PersonalityType.AGGRESSIVE),
            ("引言写手", "写200字引人入胜的开头", PersonalityType.HUMOROUS),
            ("正文作者", "写1500字深度正文", PersonalityType.ANALYTICAL),
            ("结尾升华", "写100字金句结尾", PersonalityType.MEDIATOR),
            ("排版编辑", "整体优化排版", PersonalityType.CAUTIOUS)
        ]
        
        accumulated_content = f"主题：{topic}\n要求：{requirements}\n\n"
        
        for i, (role, task, personality) in enumerate(stages, 1):
            if progress_callback:
                progress_callback(f"stage{i}", f"{role}正在{task}...", {})
            
            agent = MockAgent(role, personality)
            prompt = f"""你是一位{role}。
{task}

上下文：
{accumulated_content[:500]}...

请输出你的创作内容。"""
            
            result = await agent.generate(prompt)
            self.results["stages"][role] = {"agent": role, "content": result}
            accumulated_content += f"\n\n【{role}】\n{result}"
            
            if progress_callback:
                progress_callback(f"stage{i}_complete", f"{role}完成", {"content": result[:150]})
        
        self.results["final_content"] = accumulated_content
        self.results["end_time"] = datetime.now().isoformat()
        
        if progress_callback:
            progress_callback("complete", "公众号文章创作完成", self.results)
        
        return self.results
    
    async def _write_ecommerce(self, topic: str, requirements: str, 
                              progress_callback) -> Dict:
        """电商爆款文案创作"""
        
        if progress_callback:
            progress_callback("stage1", "市场调研员正在分析痛点...", {})
        
        # 阶段1: 痛点分析
        researcher = MockAgent("市场调研员", PersonalityType.ANALYTICAL)
        research_prompt = f"""分析以下产品的目标用户痛点：

产品：{topic}

请列出：
1. 目标用户画像
2. 核心痛点（3-5个）
3. 产品核心卖点（3-5个）
4. 竞品劣势"""
        
        research = await researcher.generate(research_prompt)
        self.results["stages"]["research"] = {"agent": "市场调研员", "content": research}
        
        if progress_callback:
            progress_callback("stage2", "文案高手正在创作...", {})
        
        # 阶段2: 文案创作
        copywriter = MockAgent("文案高手", PersonalityType.AGGRESSIVE)
        copy_prompt = f"""基于以下研究，创作电商详情页文案：

{research}

要求：
- 主标题：痛点+解决方案
- 副标题：核心卖点
- 正文：场景化描述+卖点展开
- 促销话术：紧迫感+稀缺性
- 行动号召：立即购买"""
        
        copy = await copywriter.generate(copy_prompt)
        self.results["stages"]["copy"] = {"agent": "文案高手", "content": copy}
        
        self.results["final_content"] = copy
        self.results["end_time"] = datetime.now().isoformat()
        
        if progress_callback:
            progress_callback("complete", "电商文案创作完成", self.results)
        
        return self.results


# 导出主要类
__all__ = ['HierarchyMode', 'CreativeWritingMode']
