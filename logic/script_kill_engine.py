"""
AI-Orchestra: 剧本杀游戏引擎
完整实现剧本杀游戏流程
"""

import asyncio
import random
import json
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.base_agent import MockAgent, PersonalityType


class ScriptGenre(Enum):
    """剧本类型"""
    ANCIENT = "古风悬疑"      # 古代背景
    MODERN = "现代推理"       # 现代背景
    FUTURE = "科幻未来"       # 科幻背景
    HORROR = "恐怖惊悚"       # 恐怖背景
    ROMANCE = "情感沉浸"      # 情感本


class GamePhase(Enum):
    """游戏阶段"""
    INTRO = "剧本介绍"        # 阅读剧本背景
    ROLE_READ = "角色阅读"     # 阅读个人剧本
    ROUND_1 = "第一轮搜证"     # 公开线索
    DISCUSS_1 = "第一轮讨论"   # 公聊
    ROUND_2 = "第二轮搜证"     # 深入线索
    DISCUSS_2 = "第二轮讨论"   # 深入讨论
    PRIVATE_CHAT = "私聊阶段"  # 私聊环节
    FINAL_DISCUSS = "最终讨论" # 最终公聊
    VOTE = "指认凶手"         # 投票阶段
    REVEAL = "真相揭晓"       # 公布真相
    ENDING = "结局"          # 个人结局


class ClueType(Enum):
    """线索类型"""
    PUBLIC = "公开线索"       # 所有人可见
    PRIVATE = "个人线索"      # 只有发现者可见
    SECRET = "秘密线索"       # 需要特殊条件解锁


@dataclass
class Clue:
    """线索数据结构"""
    id: str
    name: str
    description: str
    clue_type: ClueType
    location: str           # 线索所在地点
    related_roles: List[str] = field(default_factory=list)  # 相关角色
    unlock_condition: Optional[str] = None  # 解锁条件
    is_discovered: bool = False
    discovered_by: Optional[str] = None


@dataclass
class RoleScript:
    """角色剧本"""
    role_name: str
    display_name: str       # 对外显示的名字（可能有假名）
    true_identity: str      # 真实身份
    background: str         # 背景故事
    secrets: List[str]      # 个人秘密（需要隐藏）
    goals: List[str]        # 个人任务目标
    public_info: str        # 公开信息
    special_ability: Optional[str] = None  # 特殊能力
    is_murderer: bool = False  # 是否是凶手
    alibi: str = ""         # 不在场证明


@dataclass
class MurderScript:
    """凶案剧本"""
    victim_name: str
    victim_background: str
    murder_method: str
    murder_time: str
    murder_location: str
    real_murderer: str      # 真实凶手角色名
    murder_motive: str
    key_evidence: List[str]  # 关键证据
    red_herrings: List[str]  # 误导线索


@dataclass
class Script:
    """完整剧本"""
    id: str
    title: str
    genre: ScriptGenre
    difficulty: int         # 1-5难度
    player_count: int
    duration: str           # 预计时长
    background_story: str   # 剧本背景
    murder: MurderScript
    roles: Dict[str, RoleScript]
    clues: Dict[str, Clue]
    locations: List[str]    # 可搜证地点
    timeline: List[str]     # 案发时间线
    endings: Dict[str, str]  # 不同结局


# ==================== 预设剧本库 ====================

SCRIPTS_LIBRARY = {
    "ancient_mansion": Script(
        id="ancient_mansion",
        title="古宅迷踪",
        genre=ScriptGenre.ANCIENT,
        difficulty=3,
        player_count=6,
        duration="2-3小时",
        background_story="""清朝末年，江南首富沈家大院。

今日是沈老爷六十大寿，各方宾客云集。然而寿宴进行到一半，沈老爷被发现死在书房中，胸口插着一把匕首。

警方封锁了古宅，凶手就在今日在场的六人之中...

古宅中隐藏着沈家百年的秘密，每个人都有不为人知的故事。
今夜，真相将被揭开。""",
        murder=MurderScript(
            victim_name="沈万三（沈老爷）",
            victim_background="江南首富，六十大寿，性格严厉，掌控欲强",
            murder_method="匕首刺入胸口，一击致命",
            murder_time="酉时三刻（约18:45）",
            murder_location="沈家书房",
            real_murderer="沈少爷",  # 需要隐藏
            murder_motive="继承家产，摆脱父亲控制",
            key_evidence=["书房地上的玉佩", "匕首上的指纹", "少爷衣服上的血迹"],
            red_herrings=["管家的债务", "二姨太的外遇", "客人的商业纠纷"]
        ),
        roles={
            "沈少爷": RoleScript(
                role_name="沈少爷",
                display_name="沈少爷（沈老爷独子）",
                true_identity="沈家独子，实际为私生子",
                background="沈家独子，从小被严厉管教，对父亲既怕又恨。最近得知自己其实是父亲的私生子，真正的嫡子早已夭折。",
                secrets=[
                    "你是私生子，不是正室所生",
                    "你欠下巨额赌债，急需继承家产",
                    "案发时你确实在书房与父亲争吵"
                ],
                goals=[
                    "隐藏私生子身份",
                    "隐藏杀人的事实（如果你是凶手）",
                    "找出真凶（如果你不是凶手）"
                ],
                public_info="沈家独子，今日为父亲祝寿",
                is_murderer=True,
                alibi="声称在花园散步，但无人证明"
            ),
            "二姨太": RoleScript(
                role_name="二姨太",
                display_name="柳如烟（二姨太）",
                true_identity="沈老爷的二姨太，曾是戏班花旦",
                background="十年前被沈老爷纳为二姨太，一直想要个孩子稳固地位。与府中管事有暧昧关系。",
                secrets=[
                    "你与管事有私情",
                    "你偷了沈老爷的房契准备私奔",
                    "你曾威胁要公开沈少爷的身世"
                ],
                goals=[
                    "隐藏与管事的私情",
                    "找回丢失的房契",
                    "找出真凶"
                ],
                public_info="沈老爷的二姨太，温柔贤惠",
                alibi="在厨房监督寿宴准备，有下人证明"
            ),
            "管家": RoleScript(
                role_name="管家",
                display_name="福伯（沈府管家）",
                true_identity="沈家老仆，在府中30年",
                background="沈家老管家，知道沈家所有秘密。因儿子生病欠下巨债，偷偷挪用公款。",
                secrets=[
                    "你挪用了沈府5000两白银",
                    "你知道沈少爷是私生子的秘密",
                    "你曾威胁沈老爷要公开这个秘密"
                ],
                goals=[
                    "隐藏挪用公款的事",
                    "保住管家的职位",
                    "找出真凶"
                ],
                public_info="沈府老管家，忠心耿耿30年",
                alibi="在大厅接待宾客，有多人证明"
            ),
            "赵掌柜": RoleScript(
                role_name="赵掌柜",
                display_name="赵富贵（钱庄掌柜）",
                true_identity="城里钱庄掌柜，沈家的债主",
                background="沈家最大的债主，沈老爷欠钱庄十万两。今日来祝寿实为催债。",
                secrets=[
                    "沈老爷欠你十万两，已到期三个月",
                    "你带了借据来，准备今日当众逼债",
                    "你曾威胁要查封沈家产业"
                ],
                goals=[
                    "收回欠款",
                    "如果沈老爷死了，找继承人讨债",
                    "找出真凶"
                ],
                public_info="城里钱庄掌柜，沈老爷的故交",
                alibi="在客厅与其他宾客交谈"
            ),
            "李大夫": RoleScript(
                role_name="李大夫",
                display_name="李时珍（游方郎中）",
                true_identity="江湖游医，实际是为沈老爷看过病的医生",
                background="三个月前为沈老爷诊病，发现沈老爷中毒。被沈老爷重金封口。",
                secrets=[
                    "沈老爷三个月前中了慢性毒",
                    "你收了一百两封口费",
                    "你发现沈少爷在打听毒药的事"
                ],
                goals=[
                    "隐藏收钱封口的事",
                    "找出真正的凶手",
                    "自保"
                ],
                public_info="游方郎中，碰巧路过前来祝寿",
                special_ability="可以验尸获得额外线索（一次）",
                alibi="在偏厅给下人看病"
            ),
            "小翠": RoleScript(
                role_name="小翠",
                display_name="小翠（丫鬟）",
                true_identity="沈府丫鬟，二姨太的贴身侍女",
                background="二姨太的贴身丫鬟，偶然听到很多秘密。暗恋沈少爷。",
                secrets=[
                    "你偷听到二姨太和管事的私情",
                    "你知道二姨太偷房契的事",
                    "你看到沈少爷案发前进入书房"
                ],
                goals=[
                    "保护沈少爷",
                    "隐藏自己看到的事",
                    "找出真凶"
                ],
                public_info="二姨太的贴身丫鬟",
                alibi="在二姨太房里收拾，二姨太可以证明"
            )
        },
        clues={
            # 书房线索
            "clue_1": Clue("clue_1", "染血的匕首", 
                "凶器，匕首柄上有半个指纹，是沈家特制的裁纸刀", 
                ClueType.PUBLIC, "书房"),
            "clue_2": Clue("clue_2", "地上的玉佩", 
                "沈少爷随身携带的玉佩，掉落在尸体旁", 
                ClueType.PUBLIC, "书房", related_roles=["沈少爷"]),
            "clue_3": Clue("clue_3", "翻倒的茶杯", 
                "地上有打翻的茶杯，茶水有毒（与李大夫有关）", 
                ClueType.PUBLIC, "书房"),
            "clue_4": Clue("clue_4", "撕碎的借据", 
                "书房抽屉里撕碎的借据，显示沈老爷欠赵掌柜十万两", 
                ClueType.SECRET, "书房", unlock_condition="搜索书房抽屉"),
            
            # 花园线索
            "clue_5": Clue("clue_5", "泥泞的脚印", 
                "花园到书房的路上有新鲜的泥泞脚印，尺寸是男鞋", 
                ClueType.PUBLIC, "花园"),
            "clue_6": Clue("clue_6", "丢弃的手帕", 
                "手帕上绣着柳字，有血迹", 
                ClueType.PRIVATE, "花园", related_roles=["二姨太"]),
            
            # 厨房线索
            "clue_7": Clue("clue_7", "奇怪的汤药", 
                "厨房有熬了一半的毒药，经检验是慢性毒药", 
                ClueType.SECRET, "厨房", related_roles=["李大夫"]),
            
            # 客房线索
            "clue_8": Clue("clue_8", "赵掌柜的账本", 
                "账本记录沈家欠款已逾期三个月，利息惊人", 
                ClueType.PRIVATE, "客房", related_roles=["赵掌柜"]),
            
            # 下人房线索
            "clue_9": Clue("clue_9", "管家的信件", 
                "催债的信件，显示管家儿子重病急需用钱", 
                ClueType.SECRET, "下人房", related_roles=["管家"]),
        },
        locations=["书房", "花园", "厨房", "客厅", "客房", "下人房", "大厅"],
        timeline=[
            "酉时（18:00）：寿宴开始",
            "酉时一刻（18:15）：沈老爷离席去书房",
            "酉时二刻（18:30）：沈少爷离席",
            "酉时三刻（18:45）：沈老爷被发现死亡",
            "戌时（19:00）：寿宴终止，警方封锁"
        ],
        endings={
            "correct": "凶手被成功指认！沈少爷的罪行被揭露，最终被官府逮捕。沈家产业由旁支继承。",
            "wrong": "真凶逃脱！沈少爷继承了家产，但他的罪行终有一天会被揭露...",
            "alternative": "虽然没抓到凶手，但你发现了沈家的诸多秘密，这些秘密足以让沈家身败名裂。"
        }
    ),
    
    "modern_office": Script(
        id="modern_office",
        title="办公室疑云",
        genre=ScriptGenre.MODERN,
        difficulty=2,
        player_count=5,
        duration="1.5-2小时",
        background_story="""某互联网公司CEO张明被发现死在办公室内。

死者身中数刀，办公室被翻得乱七八糟。公司最近正在筹备上市，死者的死让所有人都成了嫌疑人。

凶手就在公司的五位高管之中...""",
        murder=MurderScript(
            victim_name="张明（CEO）",
            victim_background="科技公司CEO，48岁，性格强势，即将带领公司上市",
            murder_method="水果刀刺入腹部三次",
            murder_time="昨晚21:00-22:00",
            murder_location="CEO办公室",
            real_murderer="CTO",  # CTO是凶手
            murder_motive="股权纠纷，CEO准备稀释CTO股份",
            key_evidence=["CTO衣服上的血迹", "办公室监控", "股权转让协议"],
            red_herrings=["CFO的贪污", "HR的情感纠葛", "销售的业绩造假"]
        ),
        roles={
            "CTO": RoleScript(
                role_name="CTO",
                display_name="王技术（CTO）",
                true_identity="公司CTO，技术大牛，联合创始人",
                background="公司联合创始人，持股20%。CEO最近准备引入新投资人，要稀释他的股份到5%。",
                secrets=[
                    "CEO要把你的股份从20%稀释到5%",
                    "你昨晚去过CEO办公室",
                    "你在公司服务器上留了后门"
                ],
                goals=["隐藏稀释股份的矛盾", "隐藏杀人的事实", "保住自己的股份"],
                public_info="公司CTO，技术大牛",
                is_murderer=True,
                alibi="声称在写代码，但没人证明"
            ),
            "CFO": RoleScript(
                role_name="CFO",
                display_name="李财务（CFO）",
                true_identity="公司CFO，掌管财务",
                background="公司CFO，发现公司账目有问题，私自挪用了50万。",
                secrets=["挪用公款50万", "做假账掩盖", "CEO发现了账目问题"],
                goals=["隐藏挪用公款", "销毁证据", "找出真凶"],
                public_info="公司CFO，掌管财务大权",
                alibi="在家陪家人，家人可以证明"
            ),
            "HR": RoleScript(
                role_name="HR",
                display_name="张人力（HR总监）",
                true_identity="HR总监，与CEO有不正当关系",
                background="HR总监，与CEO保持了3年地下情。最近CEO要和她分手。",
                secrets=["与CEO有地下情", "CEO要分手", "你怀孕了（CEO的）"],
                goals=["隐藏地下情", "隐藏怀孕", "找出真凶"],
                public_info="公司HR总监，雷厉风行",
                alibi="在健身房，有打卡记录"
            ),
            "销售总监": RoleScript(
                role_name="销售总监",
                display_name="赵销售（销售总监）",
                true_identity="销售总监，业绩造假",
                background="销售总监，为了保住位置，伪造了大客户合同。CEO发现了端倪。",
                secrets=["伪造大客户合同", "虚报业绩30%", "CEO要查你"],
                goals=["隐藏业绩造假", "保住工作", "找出真凶"],
                public_info="公司销售总监，业绩冠军",
                alibi="在见客户，客户可以证明"
            ),
            "产品经理": RoleScript(
                role_name="产品经理",
                display_name="刘产品（产品总监）",
                true_identity="产品总监，发现CEO剽窃了他的创意",
                background="产品总监，发现CEO把他设计的产品方案给竞争对手看了。",
                secrets=["CEO剽窃你的创意", "你准备跳槽去竞品公司", "你备份了证据"],
                goals=["隐藏跳槽计划", "拿回证据", "找出真凶"],
                public_info="公司产品总监",
                alibi="在家打游戏，游戏记录可以证明"
            )
        },
        clues={
            "clue_1": Clue("clue_1", "股权转让协议", 
                "CEO办公室发现准备签署的股权变更协议，CTO股份将被稀释", 
                ClueType.PUBLIC, "办公室", related_roles=["CTO"]),
            "clue_2": Clue("clue_2", "带血的衬衫", 
                "CTO办公室垃圾桶发现的衬衫，袖口有血迹", 
                ClueType.SECRET, "CTO办公室", related_roles=["CTO"]),
            "clue_3": Clue("clue_3", "假账U盘", 
                "CFO办公桌藏着的U盘，里面有真实的账目", 
                ClueType.SECRET, "财务室", related_roles=["CFO"]),
            "clue_4": Clue("clue_4", "暧昧短信", 
                "HR手机里和CEO的暧昧短信记录", 
                ClueType.PRIVATE, "HR办公室", related_roles=["HR"]),
            "clue_5": Clue("clue_5", "伪造合同", 
                "销售部抽屉里发现的大客户合同，经核实是伪造的", 
                ClueType.SECRET, "销售部", related_roles=["销售总监"]),
            "clue_6": Clue("clue_6", "监控录像", 
                "走廊监控显示昨晚21:30有人进入CEO办公室", 
                ClueType.PUBLIC, "监控室"),
        },
        locations=["办公室", "CTO办公室", "财务室", "HR办公室", "销售部", "产品部", "监控室"],
        timeline=[
            "20:00：CTO和CEO在会议室争吵",
            "21:00：HR离开公司",
            "21:30：监控显示有人进入CEO办公室",
            "22:00：保安发现CEO死亡"
        ],
        endings={
            "correct": "CTO被成功指认！他的罪行被揭露，警方以故意杀人罪逮捕了他。",
            "wrong": "真凶逃脱！公司上市成功，但真相被永远掩盖...",
            "alternative": "你发现了公司内部的诸多腐败，决定举报给证监会。"
        }
    )
}


class ScriptKillEngine:
    """
    剧本杀游戏引擎
    """
    
    def __init__(self, script_id: str = "ancient_mansion"):
        self.script = SCRIPTS_LIBRARY.get(script_id)
        if not self.script:
            raise ValueError(f"未知剧本: {script_id}")
        
        self.players: Dict[str, MockAgent] = {}  # role_name -> agent
        self.player_assignments: Dict[str, str] = {}  # player_id -> role_name
        self.current_phase = GamePhase.INTRO
        self.round = 0
        self.discovered_clues: Dict[str, Clue] = {}
        self.votes: Dict[str, str] = {}  # voter -> suspect
        self.game_log: List[Dict] = []
        self.chat_history: List[Dict] = []  # 聊天记录
        
    def setup_game(self, player_count: Optional[int] = None) -> Dict:
        """初始化游戏"""
        if player_count is None:
            player_count = self.script.player_count
        
        # 分配角色
        available_roles = list(self.script.roles.keys())[:player_count]
        random.shuffle(available_roles)
        
        for i, role_name in enumerate(available_roles):
            player_id = f"玩家{i+1}"
            role_script = self.script.roles[role_name]
            
            # 为每个角色创建AI代理，根据角色特点分配性格
            personality = self._assign_personality(role_script)
            agent = MockAgent(role_name, personality)
            
            self.players[role_name] = agent
            self.player_assignments[player_id] = role_name
        
        self._log("system", f"游戏开始：{self.script.title}")
        self._log("system", f"参与玩家：{len(self.players)}人")
        
        return {
            "script": {
                "title": self.script.title,
                "genre": self.script.genre.value,
                "background": self.script.background_story
            },
            "players": [
                {
                    "id": pid,
                    "role": role,
                    "display_name": self.script.roles[role].display_name
                }
                for pid, role in self.player_assignments.items()
            ]
        }
    
    def _assign_personality(self, role_script: RoleScript) -> PersonalityType:
        """根据角色特点分配性格"""
        if role_script.is_murderer:
            # 凶手倾向于谨慎或激进
            return random.choice([PersonalityType.CAUTIOUS, PersonalityType.AGGRESSIVE])
        elif "丫鬟" in role_script.role_name or "仆" in role_script.role_name:
            # 仆人倾向于谨慎
            return PersonalityType.CAUTIOUS
        elif "少爷" in role_script.role_name or "CEO" in role_script.role_name:
            # 上位者倾向于激进或学霸
            return random.choice([PersonalityType.AGGRESSIVE, PersonalityType.ANALYTICAL])
        else:
            return random.choice(list(PersonalityType))
    
    def get_role_script(self, role_name: str) -> Optional[RoleScript]:
        """获取角色剧本"""
        return self.script.roles.get(role_name)
    
    async def search_clue(self, role_name: str, location: str) -> Optional[Clue]:
        """搜证"""
        # 查找该地点的未发现的线索
        available_clues = [
            clue for clue in self.script.clues.values()
            if clue.location == location and not clue.is_discovered
        ]
        
        if not available_clues:
            return None
        
        # 随机发现一条线索
        clue = random.choice(available_clues)
        clue.is_discovered = True
        clue.discovered_by = role_name
        self.discovered_clues[clue.id] = clue
        
        self._log(role_name, f"在{location}发现了线索：{clue.name}")
        
        return clue
    
    async def discuss(self, role_name: str, topic: str, context: str = "") -> str:
        """角色讨论发言"""
        agent = self.players.get(role_name)
        role_script = self.script.roles.get(role_name)
        
        if not agent or not role_script:
            return "[错误：角色不存在]"
        
        # 构建发言提示
        prompt = f"""你是{role_script.display_name}，性格{agent.personality.value}。

你的背景：{role_script.background}
你的秘密：{'；'.join(role_script.secrets[:2])}（需要隐藏）
你的目标：{'；'.join(role_script.goals)}

当前讨论话题：{topic}
上下文：{context}

已发现的线索：{'；'.join([c.name for c in self.discovered_clues.values()])}

请发表你的看法（可以只说部分真相，可以隐瞒，可以说谎）："""
        
        response = await agent.generate(prompt)
        
        self._log(role_name, f"发言：{response[:100]}...")
        self.chat_history.append({
            "role": role_name,
            "content": response,
            "type": "public",
            "time": datetime.now().isoformat()
        })
        
        return response
    
    async def private_chat(self, from_role: str, to_role: str, message: str) -> str:
        """私聊"""
        from_agent = self.players.get(from_role)
        to_agent = self.players.get(to_role)
        
        if not from_agent or not to_agent:
            return "[错误：角色不存在]"
        
        # 记录私聊
        self.chat_history.append({
            "from": from_role,
            "to": to_role,
            "content": message,
            "type": "private",
            "time": datetime.now().isoformat()
        })
        
        # 生成回复
        to_role_script = self.script.roles[to_role]
        prompt = f"""你是{to_role_script.display_name}。

{from_role}悄悄对你说："{message}"

你如何回应？（考虑你们的关系和你的秘密）"""
        
        response = await to_agent.generate(prompt)
        
        self.chat_history.append({
            "from": to_role,
            "to": from_role,
            "content": response,
            "type": "private",
            "time": datetime.now().isoformat()
        })
        
        return response
    
    def vote(self, voter_role: str, suspect_role: str) -> bool:
        """投票指认凶手"""
        self.votes[voter_role] = suspect_role
        self._log(voter_role, f"投票指认{suspect_role}为凶手")
        
        # 检查是否所有人都投票了
        return len(self.votes) == len(self.players)
    
    def get_vote_result(self) -> Dict:
        """获取投票结果"""
        if len(self.votes) < len(self.players):
            return {"status": "waiting", "votes": len(self.votes), "total": len(self.players)}
        
        # 统计票数
        vote_count: Dict[str, int] = {}
        for suspect in self.votes.values():
            vote_count[suspect] = vote_count.get(suspect, 0) + 1
        
        # 找出得票最多的
        max_votes = max(vote_count.values())
        top_suspects = [s for s, v in vote_count.items() if v == max_votes]
        
        # 真实凶手
        real_murderer = self.script.murder.real_murderer
        
        # 判断结果
        is_correct = real_murderer in top_suspects and len(top_suspects) == 1
        
        return {
            "status": "completed",
            "vote_count": vote_count,
            "top_suspects": top_suspects,
            "real_murderer": real_murderer,
            "is_correct": is_correct,
            "ending": self._get_ending(is_correct)
        }
    
    def _get_ending(self, is_correct: bool) -> str:
        """获取结局"""
        if is_correct:
            return self.script.endings["correct"]
        else:
            return self.script.endings["wrong"]
    
    def reveal_truth(self) -> Dict:
        """揭晓真相"""
        murder = self.script.murder
        
        return {
            "victim": murder.victim_name,
            "murderer": murder.real_murderer,
            "method": murder.murder_method,
            "time": murder.murder_time,
            "location": murder.murder_location,
            "motive": murder.murder_motive,
            "key_evidence": murder.key_evidence,
            "timeline": self.script.timeline
        }
    
    def _log(self, source: str, content: str):
        """记录日志"""
        self.game_log.append({
            "time": datetime.now().isoformat(),
            "source": source,
            "content": content
        })
    
    def get_game_summary(self) -> str:
        """获取游戏总结"""
        lines = [
            f"═══ {self.script.title} 游戏记录 ═══",
            f"剧本类型：{self.script.genre.value}",
            f"参与人数：{len(self.players)}",
            f"",
            "【游戏日志】"
        ]
        
        for log in self.game_log:
            lines.append(f"[{log['source']}] {log['content']}")
        
        if self.votes:
            lines.extend([
                "",
                "【投票结果】",
                f"指认结果：{self.get_vote_result()}"
            ])
        
        return "\n".join(lines)


# 导出
__all__ = ['ScriptKillEngine', 'Script', 'RoleScript', 'Clue', 'ScriptGenre', 'GamePhase']
