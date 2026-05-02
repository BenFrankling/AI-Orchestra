"""
AI-Orchestra: 狼人杀游戏引擎
完整实现狼人杀游戏流程
"""

import asyncio
import random
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from core.base_agent import MockAgent, PersonalityType


class Role(Enum):
    """狼人杀角色"""
    WEREWOLF = "狼人"
    VILLAGER = "平民"
    PROPHET = "预言家"
    WITCH = "女巫"
    HUNTER = "猎人"
    JUDGE = "法官"


class GamePhase(Enum):
    """游戏阶段"""
    SETUP = "准备阶段"
    NIGHT_WEREWOLF = "狼人行动"
    NIGHT_PROPHET = "预言家行动"
    NIGHT_WITCH = "女巫行动"
    DAY_ANNOUNCE = "天亮公布"
    DAY_DISCUSS = "白天讨论"
    DAY_VOTE = "投票处决"
    GAME_OVER = "游戏结束"


class Team(Enum):
    """阵营"""
    GOOD = "好人阵营"
    EVIL = "狼人阵营"


@dataclass
class Player:
    """玩家数据结构"""
    id: int
    name: str
    role: Role
    personality: PersonalityType
    is_alive: bool = True
    is_revealed: bool = False  # 身份是否已暴露
    
    # 技能状态
    can_use_skill: bool = True  # 是否还能使用技能
    poison_used: bool = False   # 女巫是否用过毒药
    antidote_used: bool = False # 女巫是否用过解药
    
    # 游戏状态
    votes_received: int = 0
    voted_for: Optional[int] = None
    
    def __post_init__(self):
        self.agent = MockAgent(self.name, self.personality)
        self.team = Team.EVIL if self.role == Role.WEREWOLF else Team.GOOD
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value if self.is_revealed else "???",
            "personality": self.personality.value,
            "is_alive": self.is_alive,
            "team": self.team.value if self.is_revealed else "???"
        }


@dataclass
class GameLog:
    """游戏日志"""
    round: int
    phase: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            "round": self.round,
            "phase": self.phase,
            "content": self.content,
            "timestamp": self.timestamp
        }


class WerewolfEngine:
    """
    狼人杀游戏引擎
    完整实现狼人杀游戏流程
    """
    
    def __init__(self, num_players: int = 10, random_seed: Optional[int] = None):
        self.num_players = num_players
        self.random_seed = random_seed or random.randint(1, 10000)
        random.seed(self.random_seed)
        
        self.players: Dict[int, Player] = {}
        self.alive_players: List[int] = []
        self.dead_players: List[int] = []
        
        self.current_round = 0
        self.current_phase = GamePhase.SETUP
        self.game_over = False
        self.winner: Optional[Team] = None
        
        self.logs: List[GameLog] = []
        self.night_deaths: List[int] = []  # 今晚死亡的人
        self.last_words: Dict[int, str] = {}  # 遗言
        
        # 特殊角色记录
        self.werewolves: List[int] = []
        self.prophet: Optional[int] = None
        self.witch: Optional[int] = None
        self.hunter: Optional[int] = None
        
        # 游戏状态
        self.vote_results: Dict[int, int] = {}  # 投票结果
        self.check_results: Dict[int, Tuple[int, Team]] = {}  # 预言家验人结果
    
    def setup_game(self, player_names: Optional[List[str]] = None) -> Dict:
        """
        初始化游戏
        
        Returns:
            游戏初始状态
        """
        self._log(0, GamePhase.SETUP.value, f"游戏初始化，随机种子: {self.random_seed}")
        
        # 生成玩家名字
        if not player_names:
            player_names = [f"AI-{i+1}" for i in range(self.num_players)]
        
        # 角色分配
        roles = self._distribute_roles()
        
        # 创建玩家
        for i in range(self.num_players):
            personality = random.choice(list(PersonalityType))
            player = Player(
                id=i,
                name=player_names[i],
                role=roles[i],
                personality=personality
            )
            self.players[i] = player
            self.alive_players.append(i)
            
            # 记录特殊角色
            if roles[i] == Role.WEREWOLF:
                self.werewolves.append(i)
            elif roles[i] == Role.PROPHET:
                self.prophet = i
            elif roles[i] == Role.WITCH:
                self.witch = i
            elif roles[i] == Role.HUNTER:
                self.hunter = i
            
            self._log(0, GamePhase.SETUP.value, 
                     f"{player.name} -> {roles[i].value} ({personality.value})")
        
        self._log(0, GamePhase.SETUP.value, 
                 f"角色分配完成: 狼人{len(self.werewolves)}人, 平民{self.num_players - len(self.werewolves) - 3}人, 神职3人")
        
        return self.get_game_state()
    
    def _distribute_roles(self) -> List[Role]:
        """分配角色"""
        # 根据人数调整角色配置
        if self.num_players == 10:
            roles = [Role.WEREWOLF] * 2 + [Role.VILLAGER] * 5 + [Role.PROPHET, Role.WITCH, Role.HUNTER]
        elif self.num_players == 9:
            roles = [Role.WEREWOLF] * 2 + [Role.VILLAGER] * 4 + [Role.PROPHET, Role.WITCH, Role.HUNTER]
        elif self.num_players == 8:
            roles = [Role.WEREWOLF] * 2 + [Role.VILLAGER] * 4 + [Role.PROPHET, Role.WITCH]
        elif self.num_players == 12:
            roles = [Role.WEREWOLF] * 3 + [Role.VILLAGER] * 6 + [Role.PROPHET, Role.WITCH, Role.HUNTER]
        else:
            # 默认配置：狼人占1/4，其他为平民和神职
            werewolf_count = max(2, self.num_players // 4)
            villager_count = self.num_players - werewolf_count - 3
            roles = [Role.WEREWOLF] * werewolf_count + [Role.VILLAGER] * villager_count
            roles += [Role.PROPHET, Role.WITCH, Role.HUNTER]
        
        random.shuffle(roles)
        return roles
    
    async def play_round(self, progress_callback=None) -> Dict:
        """
        进行一轮游戏（一天一夜）
        
        Returns:
            本轮游戏结果
        """
        self.current_round += 1
        self.night_deaths = []
        
        if progress_callback:
            progress_callback("round_start", f"第{self.current_round}天开始", {"round": self.current_round})
        
        # ===== 夜晚阶段 =====
        # 1. 狼人行动
        await self._night_werewolf(progress_callback)
        
        # 2. 预言家行动
        await self._night_prophet(progress_callback)
        
        # 3. 女巫行动
        await self._night_witch(progress_callback)
        
        # ===== 白天阶段 =====
        # 4. 天亮公布
        await self._day_announce(progress_callback)
        
        # 检查游戏是否结束
        if self._check_game_over():
            return self.get_game_state()
        
        # 5. 白天讨论
        await self._day_discuss(progress_callback)
        
        # 6. 投票处决
        await self._day_vote(progress_callback)
        
        # 检查游戏是否结束
        self._check_game_over()
        
        return self.get_game_state()
    
    async def _night_werewolf(self, progress_callback):
        """狼人夜晚行动"""
        self.current_phase = GamePhase.NIGHT_WEREWOLF
        
        alive_werewolves = [wid for wid in self.werewolves if self.players[wid].is_alive]
        alive_good = [pid for pid in self.alive_players if self.players[pid].team == Team.GOOD]
        
        if not alive_werewolves or not alive_good:
            return
        
        if progress_callback:
            progress_callback("night_werewolf", "🐺 狼人正在商量...", 
                            {"werewolves": [self.players[wid].name for wid in alive_werewolves]})
        
        # 狼人讨论并选择目标
        # 简化逻辑：随机选择或根据性格选择
        target = self._werewolf_select_target(alive_werewolves, alive_good)
        
        # 记录狼人行动
        werewolf_names = ", ".join([self.players[wid].name for wid in alive_werewolves])
        self._log(self.current_round, GamePhase.NIGHT_WEREWOLF.value,
                 f"狼人({werewolf_names})选择刀: {self.players[target].name}")
        
        # 暂时标记为死亡（等待女巫救）
        self.night_deaths.append(target)
    
    def _werewolf_select_target(self, werewolves: List[int], targets: List[int]) -> int:
        """狼人选择目标策略"""
        # 激进型狼人倾向于刀明神
        # 谨慎型狼人倾向于刀民
        # 可以加入更复杂的策略
        
        # 优先刀神职（如果有线索）
        important_roles = [self.prophet, self.witch, self.hunter]
        for role_id in important_roles:
            if role_id in targets and random.random() > 0.3:  # 70%概率刀神
                return role_id
        
        return random.choice(targets)
    
    async def _night_prophet(self, progress_callback):
        """预言家夜晚行动"""
        if self.prophet is None or not self.players[self.prophet].is_alive:
            return
        
        self.current_phase = GamePhase.NIGHT_PROPHET
        
        if progress_callback:
            progress_callback("night_prophet", "🔮 预言家正在验人...", 
                            {"prophet": self.players[self.prophet].name})
        
        # 预言家选择验人目标
        alive_unknown = [pid for pid in self.alive_players 
                        if pid != self.prophet and pid not in self.check_results]
        
        if not alive_unknown:
            alive_unknown = [pid for pid in self.alive_players if pid != self.prophet]
        
        if alive_unknown:
            check_target = random.choice(alive_unknown)
            target_team = self.players[check_target].team
            
            self.check_results[check_target] = (self.current_round, target_team)
            
            team_str = "狼人" if target_team == Team.EVIL else "好人"
            self._log(self.current_round, GamePhase.NIGHT_PROPHET.value,
                     f"预言家查验 {self.players[check_target].name} -> {team_str}")
    
    async def _night_witch(self, progress_callback):
        """女巫夜晚行动"""
        if self.witch is None or not self.players[self.witch].is_alive:
            return
        
        self.current_phase = GamePhase.NIGHT_WITCH
        witch = self.players[self.witch]
        
        if progress_callback:
            progress_callback("night_witch", "🧙 女巫正在思考...", 
                            {"witch": witch.name})
        
        # 女巫决策
        if self.night_deaths:
            target = self.night_deaths[0]
            target_name = self.players[target].name
            
            # 决策逻辑：第一晚通常救人，后续根据情况
            should_save = False
            if not witch.antidote_used:
                if self.current_round == 1:  # 第一晚必救
                    should_save = True
                elif self.players[target].role in [Role.PROPHET, Role.WITCH, Role.HUNTER]:
                    should_save = True  # 救神职
                elif random.random() > 0.5:  # 随机救
                    should_save = True
            
            if should_save:
                witch.antidote_used = True
                self.night_deaths.remove(target)
                self._log(self.current_round, GamePhase.NIGHT_WITCH.value,
                         f"女巫使用解药救了 {target_name}")
            else:
                self._log(self.current_round, GamePhase.NIGHT_WITCH.value,
                         f"女巫选择不救 {target_name}")
        
        # 毒药使用（简化逻辑）
        if not witch.poison_used and witch.antidote_used and random.random() > 0.7:
            alive_players = [pid for pid in self.alive_players if pid != self.witch]
            if alive_players:
                poison_target = random.choice(alive_players)
                witch.poison_used = True
                self.players[poison_target].is_alive = False
                self.alive_players.remove(poison_target)
                self.dead_players.append(poison_target)
                self._log(self.current_round, GamePhase.NIGHT_WITCH.value,
                         f"女巫使用毒药毒死了 {self.players[poison_target].name}")
    
    async def _day_announce(self, progress_callback):
        """天亮公布"""
        self.current_phase = GamePhase.DAY_ANNOUNCE
        
        if progress_callback:
            progress_callback("day_announce", "☀️ 天亮了...", {})
        
        # 处理夜间死亡
        if self.night_deaths:
            death_names = ", ".join([self.players[pid].name for pid in self.night_deaths])
            self._log(self.current_round, GamePhase.DAY_ANNOUNCE.value,
                     f"昨晚死亡: {death_names}")
            
            for pid in self.night_deaths:
                self.players[pid].is_alive = False
                self.alive_players.remove(pid)
                self.dead_players.append(pid)
                
                # 遗言（简化）
                if self.players[pid].role == Role.HUNTER:
                    # 猎人发动技能
                    await self._hunter_skill(pid)
        else:
            self._log(self.current_round, GamePhase.DAY_ANNOUNCE.value,
                     "昨晚是平安夜，无人死亡")
    
    async def _hunter_skill(self, hunter_id: int):
        """猎人技能"""
        hunter = self.players[hunter_id]
        if not hunter.can_use_skill:
            return
        
        # 选择带走一个人
        alive_others = [pid for pid in self.alive_players if pid != hunter_id]
        if alive_others:
            target = random.choice(alive_others)
            hunter.can_use_skill = False
            self.players[target].is_alive = False
            self.alive_players.remove(target)
            self.dead_players.append(target)
            
            self._log(self.current_round, GamePhase.DAY_ANNOUNCE.value,
                     f"猎人 {hunter.name} 发动技能带走了 {self.players[target].name}")
    
    async def _day_discuss(self, progress_callback):
        """白天讨论"""
        self.current_phase = GamePhase.DAY_DISCUSS
        
        if progress_callback:
            progress_callback("day_discuss", "💬 白天讨论开始...", 
                            {"alive_count": len(self.alive_players)})
        
        # 存活玩家轮流发言
        for pid in self.alive_players:
            player = self.players[pid]
            
            # 生成发言（基于性格和身份）
            speech = await self._generate_speech(player)
            
            self._log(self.current_round, GamePhase.DAY_DISCUSS.value,
                     f"{player.name}({player.role.value if player.is_revealed else '???'}): {speech}")
            
            if progress_callback:
                progress_callback("speech", f"{player.name} 发言", 
                                {"player": player.name, "speech": speech})
    
    async def _generate_speech(self, player: Player) -> str:
        """生成玩家发言"""
        # 根据性格和角色生成不同风格的发言
        context = self._build_speech_context(player)
        
        prompt = f"""你是{player.name}，性格{player.personality.value}，
{'身份是' + player.role.value if player.role == Role.WEREWOLF else '身份未知'}。

当前游戏状态：
{context}

请发表你的观点（30-50字）："""
        
        return await player.agent.generate(prompt)
    
    def _build_speech_context(self, player: Player) -> str:
        """构建发言上下文"""
        alive_names = [self.players[pid].name for pid in self.alive_players]
        dead_info = [f"{self.players[pid].name}({self.players[pid].role.value})" 
                    for pid in self.dead_players]
        
        context = f"存活玩家: {', '.join(alive_names)}\n"
        if dead_info:
            context += f"已死亡: {', '.join(dead_info)}\n"
        
        # 预言家添加验人信息
        if player.role == Role.PROPHET and player.is_alive:
            checks = [f"第{r}天验了{self.players[pid].name}是{t.value}" 
                     for pid, (r, t) in self.check_results.items()]
            if checks:
                context += f"验人记录: {'; '.join(checks)}\n"
        
        return context
    
    async def _day_vote(self, progress_callback):
        """投票处决"""
        self.current_phase = GamePhase.DAY_VOTE
        
        if progress_callback:
            progress_callback("day_vote", "🗳️ 投票开始...", {})
        
        # 重置投票
        for pid in self.alive_players:
            self.players[pid].votes_received = 0
            self.players[pid].voted_for = None
        
        # 每个玩家投票
        votes: Dict[int, int] = {}  # voter -> target
        
        for pid in self.alive_players:
            player = self.players[pid]
            target = self._select_vote_target(player)
            votes[pid] = target
            self.players[target].votes_received += 1
            self.players[pid].voted_for = target
        
        # 统计投票结果
        vote_details = ", ".join([f"{self.players[voter].name}->{self.players[target].name}" 
                                for voter, target in votes.items()])
        self._log(self.current_round, GamePhase.DAY_VOTE.value, f"投票详情: {vote_details}")
        
        # 找出得票最多的人
        max_votes = max([self.players[pid].votes_received for pid in self.alive_players])
        if max_votes > 0:
            candidates = [pid for pid in self.alive_players 
                         if self.players[pid].votes_received == max_votes]
            
            if len(candidates) == 1:
                executed = candidates[0]
                self.players[executed].is_alive = False
                self.alive_players.remove(executed)
                self.dead_players.append(executed)
                
                self._log(self.current_round, GamePhase.DAY_VOTE.value,
                         f"{self.players[executed].name} 被投票处决，身份是 {self.players[executed].role.value}")
                
                # 暴露身份
                self.players[executed].is_revealed = True
                
                # 猎人发动技能
                if self.players[executed].role == Role.HUNTER:
                    await self._hunter_skill(executed)
            else:
                self._log(self.current_round, GamePhase.DAY_VOTE.value,
                         f"平票: {', '.join([self.players[pid].name for pid in candidates])}，无人被处决")
    
    def _select_vote_target(self, player: Player) -> int:
        """选择投票目标"""
        # 简化逻辑：随机投票给非自己的人
        others = [pid for pid in self.alive_players if pid != player.id]
        if not others:
            return player.id
        
        # 狼人不会投票给狼队友
        if player.role == Role.WEREWOLF:
            good_players = [pid for pid in others if self.players[pid].role != Role.WEREWOLF]
            if good_players:
                return random.choice(good_players)
        
        return random.choice(others)
    
    def _check_game_over(self) -> bool:
        """检查游戏是否结束"""
        alive_werewolves = len([pid for pid in self.alive_players 
                               if self.players[pid].role == Role.WEREWOLF])
        alive_good = len([pid for pid in self.alive_players 
                         if self.players[pid].role != Role.WEREWOLF])
        
        if alive_werewolves == 0:
            self.game_over = True
            self.winner = Team.GOOD
            self._log(self.current_round, GamePhase.GAME_OVER.value,
                     "好人阵营胜利！所有狼人已被消灭")
            return True
        
        if alive_werewolves >= alive_good:
            self.game_over = True
            self.winner = Team.EVIL
            self._log(self.current_round, GamePhase.GAME_OVER.value,
                     "狼人阵营胜利！狼人数量大于等于好人")
            return True
        
        return False
    
    def _log(self, round_num: int, phase: str, content: str):
        """记录日志"""
        log = GameLog(round=round_num, phase=phase, content=content)
        self.logs.append(log)
    
    def get_game_state(self) -> Dict:
        """获取当前游戏状态"""
        return {
            "round": self.current_round,
            "phase": self.current_phase.value,
            "game_over": self.game_over,
            "winner": self.winner.value if self.winner else None,
            "alive_count": len(self.alive_players),
            "alive_players": [self.players[pid].to_dict() for pid in self.alive_players],
            "dead_players": [self.players[pid].to_dict() for pid in self.dead_players],
            "logs": [log.to_dict() for log in self.logs[-10:]]  # 最近10条
        }
    
    def get_full_logs(self) -> str:
        """获取完整游戏记录"""
        lines = [
            "=" * 50,
            "🐺 AI-Orchestra 狼人杀游戏记录",
            "=" * 50,
            f"游戏配置: {self.num_players}人局",
            f"随机种子: {self.random_seed}",
            f"{'=' * 50}\n"
        ]
        
        for log in self.logs:
            lines.append(f"[第{log.round}天 - {log.phase}] {log.content}")
        
        if self.game_over:
            lines.extend([
                "\n" + "=" * 50,
                f"🏆 游戏结束，{self.winner.value} 胜利！",
                "=" * 50
            ])
        
        return "\n".join(lines)
    
    async def run_full_game(self, max_rounds: int = 20, 
                           progress_callback=None) -> Dict:
        """
        运行完整游戏
        
        Args:
            max_rounds: 最大轮数
            progress_callback: 进度回调函数
        
        Returns:
            游戏结果
        """
        # 初始化
        self.setup_game()
        
        if progress_callback:
            progress_callback("game_start", f"游戏开始！共{self.num_players}人", 
                            {"players": [p.to_dict() for p in self.players.values()]})
        
        # 游戏循环
        while not self.game_over and self.current_round < max_rounds:
            await self.play_round(progress_callback)
            
            if progress_callback:
                progress_callback("round_end", f"第{self.current_round}天结束", 
                                self.get_game_state())
        
        # 游戏结束
        if not self.game_over:
            self._log(self.current_round, GamePhase.GAME_OVER.value, "达到最大回合数，游戏结束")
        
        if progress_callback:
            progress_callback("game_end", f"游戏结束，{self.winner.value}胜利！", 
                            self.get_game_state())
        
        return {
            "winner": self.winner.value if self.winner else "平局",
            "total_rounds": self.current_round,
            "logs": self.get_full_logs(),
            "final_state": self.get_game_state()
        }


# 导出
__all__ = ['WerewolfEngine', 'Role', 'GamePhase', 'Team', 'Player']
