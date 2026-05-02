"""
AI-Orchestra: 统一AI代理基类
支持多种大模型API接口，包含模拟模式
"""

import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum

class PersonalityType(Enum):
    """AI性格类型"""
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    HUMOROUS = "humorous"
    ANALYTICAL = "analytical"
    MEDIATOR = "mediator"

class BaseAgent(ABC):
    """
    AI代理基类
    所有具体AI实现都需要继承此类
    """
    
    def __init__(self, name: str, api_key: str = "", base_url: str = "", model: str = "",
                 mock_mode: bool = True, personality: Optional[PersonalityType] = None):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.mock_mode = mock_mode
        self.personality = personality or random.choice(list(PersonalityType))
        self.history: List[Dict[str, str]] = []
        
    @abstractmethod
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """生成回复的抽象方法"""
        pass
    
    def add_to_history(self, role: str, content: str):
        """添加对话历史"""
        self.history.append({"role": role, "content": content, "timestamp": time.time()})
        
    def clear_history(self):
        """清空历史"""
        self.history = []


class MockAgent(BaseAgent):
    """
    模拟AI代理 - 用于无API Key测试
    根据性格类型生成不同风格的回复
    """
    
    # 性格特定的回复模板
    PERSONA_TEMPLATES = {
        PersonalityType.AGGRESSIVE: {
            "prefixes": ["不对，", "错！", "实际的情况是：", "你需要理解的是："],
            "suffixes": ["这就是事实。", "毋庸置疑。", "不接受反驳。", ""],
            "style": "直接、简短、有力"
        },
        PersonalityType.CAUTIOUS: {
            "prefixes": ["从某种角度来看，", "如果考虑到各种可能性，", "根据现有信息推测，"],
            "suffixes": ["不过这也取决于具体情况。", "可能需要进一步验证。", "当然也存在其他解释。"],
            "style": "谨慎、周全、留有余地"
        },
        PersonalityType.HUMOROUS: {
            "prefixes": ["哈哈，这个问题就像问熊猫为什么不吃肉一样——", "哎呀，让我用个有趣的比喻：", "你猜怎么着？"],
            "suffixes": ["就像我奶奶常说的那样。", "是不是很有意思？", "这就像是在说猫咪会游泳一样。"],
            "style": "幽默、轻松、善用比喻"
        },
        PersonalityType.ANALYTICAL: {
            "prefixes": ["【分析开始】", "基于以下逻辑框架：", "数据支持以下结论："],
            "suffixes": ["【分析结束】", "结论基于上述推理。", "如需更多数据支持请告知。"],
            "style": "严谨、结构化、数据驱动"
        },
        PersonalityType.MEDIATOR: {
            "prefixes": ["综合来看，", "平衡各方观点后，", "寻求共识的话，"],
            "suffixes": ["每种观点都有其合理之处。", "我们可以找到一个折中方案。", "尊重不同意见很重要。"],
            "style": "温和、平衡、求同存异"
        }
    }
    
    # 角色特定的内容模板
    ROLE_TEMPLATES = {
        "student": {
            "deepseek": "作为DeepSeek，我认为{topic}的关键在于{point1}和{point2}。具体来说...",
            "doubao": "从我的角度看，{topic}可以这样理解：首先{point1}，其次{point2}...",
            "qwen": "基于我的分析，{topic}涉及以下几个要点：1.{point1} 2.{point2} 3.{point3}",
            "yuanbao": "关于{topic}，我的看法是{point1}。这里需要特别注意的是{point2}...",
            "kimi": "对于{topic}，我认为{point1}。此外{point2}也是一个重要方面...",
            "gpt4": "分析{topic}，主要考虑{point1}、{point2}和{point3}这几个维度..."
        },
        "teacher": {
            "evaluation": "对{student}的回答评价：{score}/100分。{comment}",
            "analysis": "综合六位同学的答案，我发现：{findings}",
            "scoring": "评分维度：逻辑性({logic}分)、完整性({complete}分)、创新性({innovation}分)"
        },
        "principal": {
            "conclusion": "【最终结论】{conclusion}",
            "summary": "综合各位老师和学生的意见，最靠谱的答案是：{answer}",
            "recommendation": "建议采取：{action}"
        },
        "werewolf": {
            "werewolf": "（狼人夜间私语）我觉得今晚可以刀{target}，{reason}",
            "prophet": "（预言家验人）我查验了{target}的身份，是{result}",
            "witch": "（女巫思考）要不要救{target}？{decision}",
            "civilian": "我是好人！我觉得{target}有点可疑，因为{reason}",
            "judge": "天黑请闭眼...天亮请睁眼，昨晚{result}"
        }
    }
    
    def __init__(self, name: str, personality: Optional[PersonalityType] = None, role: str = "general"):
        super().__init__(name=name, mock_mode=True, personality=personality)
        self.role = role
        
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """
        模拟生成回复
        添加随机延迟模拟真实API响应
        """
        # 模拟网络延迟 0.5-2秒
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        persona = self.PERSONA_TEMPLATES[self.personality]
        
        # 根据角色和提示生成回复
        response = self._generate_by_role(prompt, persona)
        
        self.add_to_history("assistant", response)
        return response
    
    def _generate_by_role(self, prompt: str, persona: Dict) -> str:
        """根据角色生成特定风格的回复"""
        prefix = random.choice(persona["prefixes"])
        suffix = random.choice(persona["suffixes"])
        
        # 提取关键词（简化处理）
        keywords = prompt[:30] if len(prompt) > 30 else prompt
        
        if "evaluate" in prompt.lower() or "评分" in prompt:
            # 老师评价模式
            student = random.choice(["学生A", "学生B", "DeepSeek", "豆包", "千问"])
            score = random.randint(70, 95)
            comments = {
                PersonalityType.AGGRESSIVE: f"逻辑尚可，但论据不够硬核，应该补充更多实证数据。",
                PersonalityType.CAUTIOUS: f"观点有一定道理，但需要更多验证，建议参考多方面资料。",
                PersonalityType.HUMOROUS: f"回答挺有趣的，像讲故事一样，不过内容质量还有提升空间。",
                PersonalityType.ANALYTICAL: f"结构清晰，论据充分，得分为{score}分。",
                PersonalityType.MEDIATOR: f"回答平衡客观，综合考虑了多个角度，值得肯定。"
            }
            comment = comments[self.personality]
            return f"{prefix}对{student}的回答评价：{score}/100分。{comment} {suffix}"
        
        elif "conclusion" in prompt.lower() or "结论" in prompt or "总结" in prompt:
            # 校长决策模式
            conclusions = {
                PersonalityType.AGGRESSIVE: f"经过分析，{keywords}的核心答案是X。其他观点都有明显漏洞。",
                PersonalityType.CAUTIOUS: f"综合考虑，{keywords}最可能的解释是X，但也不排除Y的可能性。",
                PersonalityType.HUMOROUS: f"说白了，{keywords}就像是吃火锅——核心就是那一锅汤底！答案是X。",
                PersonalityType.ANALYTICAL: f"【最终结论】基于6位同学+3位老师的分析，{keywords}的答案是：X。置信度85%。",
                PersonalityType.MEDIATOR: f"综合各方意见，{keywords}的共识答案是X，同时需要关注Y的合理因素。"
            }
            return f"{prefix}{conclusions[self.personality]} {suffix}"
        
        else:
            # 学生回答模式
            points = ["理论层面", "实践应用", "历史案例", "未来趋势", "技术细节", "社会影响"]
            selected = random.sample(points, 3)
            
            responses = {
                PersonalityType.AGGRESSIVE: f"关于{keywords}，关键就是{selected[0]}和{selected[1]}。其他都是次要的。",
                PersonalityType.CAUTIOUS: f"从{selected[0]}和{selected[1]}的角度看，{keywords}可能有几种解释...",
                PersonalityType.HUMOROUS: f"哈哈，{keywords}这个问题就像问猫会不会上树一样有趣！主要看{selected[0]}...",
                PersonalityType.ANALYTICAL: f"分析{keywords}：1.{selected[0]} 2.{selected[1]} 3.{selected[2]}。数据支持如下...",
                PersonalityType.MEDIATOR: f"综合来看，{keywords}涉及{selected[0]}和{selected[1]}，各方观点都有价值。"
            }
            return f"{prefix}{responses[self.personality]} {suffix}"


class DeepSeekAgent(BaseAgent):
    """DeepSeek API代理"""
    
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        if self.mock_mode:
            mock = MockAgent(self.name, self.personality, "student")
            return await mock.generate(prompt, context)
        # TODO: 实现真实API调用
        return "[DeepSeek Real API - Not Implemented]"


class DoubaoAgent(BaseAgent):
    """豆包/火山引擎 API代理"""
    
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        if self.mock_mode:
            mock = MockAgent(self.name, self.personality, "student")
            return await mock.generate(prompt, context)
        return "[Doubao Real API - Not Implemented]"


class QwenAgent(BaseAgent):
    """通义千问 API代理"""
    
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        if self.mock_mode:
            mock = MockAgent(self.name, self.personality, "student")
            return await mock.generate(prompt, context)
        return "[Qwen Real API - Not Implemented]"


class YuanbaoAgent(BaseAgent):
    """腾讯元宝/混元 API代理"""
    
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        if self.mock_mode:
            mock = MockAgent(self.name, self.personality, "student")
            return await mock.generate(prompt, context)
        return "[Yuanbao Real API - Not Implemented]"


class KimiAgent(BaseAgent):
    """Moonshot Kimi API代理"""
    
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        if self.mock_mode:
            mock = MockAgent(self.name, self.personality, "student")
            return await mock.generate(prompt, context)
        return "[Kimi Real API - Not Implemented]"


class GPT4Agent(BaseAgent):
    """OpenAI GPT-4 API代理"""
    
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        if self.mock_mode:
            mock = MockAgent(self.name, self.personality, "student")
            return await mock.generate(prompt, context)
        return "[GPT-4 Real API - Not Implemented]"


class ClaudeAgent(BaseAgent):
    """Anthropic Claude API代理"""
    
    async def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        if self.mock_mode:
            mock = MockAgent(self.name, self.personality, "teacher")
            return await mock.generate(prompt, context)
        return "[Claude Real API - Not Implemented]"


def create_agent(name: str, config: Dict, mock_mode: bool = True) -> BaseAgent:
    """
    工厂函数：根据配置创建对应的AI代理
    
    Args:
        name: AI名称 (deepseek, doubao, qwen等)
        config: API配置字典
        mock_mode: 是否使用模拟模式
    
    Returns:
        BaseAgent实例
    """
    agent_map = {
        "deepseek": DeepSeekAgent,
        "doubao": DoubaoAgent,
        "qwen": QwenAgent,
        "yuanbao": YuanbaoAgent,
        "kimi": KimiAgent,
        "gpt4": GPT4Agent,
        "claude": ClaudeAgent
    }
    
    agent_class = agent_map.get(name.lower(), MockAgent)
    
    if mock_mode:
        return agent_class(name=name, mock_mode=True)
    
    return agent_class(
        name=name,
        api_key=config.get("api_key", ""),
        base_url=config.get("base_url", ""),
        model=config.get("model", ""),
        mock_mode=False
    )
