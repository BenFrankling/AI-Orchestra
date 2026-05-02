"""
AI-Orchestra: 对话记忆系统
实现跨会话、跨游戏的AI记忆持久化
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib


@dataclass
class MemoryEntry:
    """单条记忆条目"""
    id: str
    agent_name: str              # AI代理名称
    session_id: str              # 会话ID
    memory_type: str             # 记忆类型: fact/opinion/event/preference
    content: str                 # 记忆内容
    context: str                 # 上下文（问题/场景）
    importance: int              # 重要程度 1-10
    timestamp: str
    tags: List[str]              # 标签
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryEntry":
        return cls(**data)


@dataclass
class AgentProfile:
    """AI代理档案"""
    agent_name: str
    personality: str             # 性格类型
    created_at: str
    total_interactions: int = 0
    known_facts: List[str] = None
    learned_preferences: Dict[str, Any] = None
    relationship_scores: Dict[str, int] = None  # 与其他代理的关系分
    
    def __post_init__(self):
        if self.known_facts is None:
            self.known_facts = []
        if self.learned_preferences is None:
            self.learned_preferences = {}
        if self.relationship_scores is None:
            self.relationship_scores = {}


class MemoryStore:
    """
    记忆存储
    使用SQLite持久化存储
    """
    
    def __init__(self, db_path: str = "memory/orchestra_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            # 记忆表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context TEXT,
                    importance INTEGER DEFAULT 5,
                    timestamp TEXT NOT NULL,
                    tags TEXT
                )
            """)
            
            # 代理档案表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_profiles (
                    agent_name TEXT PRIMARY KEY,
                    personality TEXT,
                    created_at TEXT,
                    total_interactions INTEGER DEFAULT 0,
                    known_facts TEXT,
                    learned_preferences TEXT,
                    relationship_scores TEXT
                )
            """)
            
            # 会话表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    session_type TEXT,
                    created_at TEXT,
                    summary TEXT
                )
            """)
            
            conn.commit()
    
    def save_memory(self, entry: MemoryEntry) -> bool:
        """保存记忆"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO memories 
                       (id, agent_name, session_id, memory_type, content, context, 
                        importance, timestamp, tags)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        entry.id, entry.agent_name, entry.session_id,
                        entry.memory_type, entry.content, entry.context,
                        entry.importance, entry.timestamp, json.dumps(entry.tags)
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"保存记忆失败: {e}")
            return False
    
    def get_memories(self, agent_name: Optional[str] = None,
                     memory_type: Optional[str] = None,
                     min_importance: int = 1,
                     limit: int = 50) -> List[MemoryEntry]:
        """获取记忆"""
        query = "SELECT * FROM memories WHERE importance >= ?"
        params = [min_importance]
        
        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)
        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                MemoryEntry(
                    id=row["id"],
                    agent_name=row["agent_name"],
                    session_id=row["session_id"],
                    memory_type=row["memory_type"],
                    content=row["content"],
                    context=row["context"],
                    importance=row["importance"],
                    timestamp=row["timestamp"],
                    tags=json.loads(row["tags"]) if row["tags"] else []
                )
                for row in rows
            ]
    
    def search_memories(self, keyword: str, limit: int = 20) -> List[MemoryEntry]:
        """搜索记忆"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM memories 
                   WHERE content LIKE ? OR context LIKE ? OR tags LIKE ?
                   ORDER BY importance DESC, timestamp DESC
                   LIMIT ?""",
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit)
            )
            rows = cursor.fetchall()
            
            return [
                MemoryEntry(
                    id=row["id"],
                    agent_name=row["agent_name"],
                    session_id=row["session_id"],
                    memory_type=row["memory_type"],
                    content=row["content"],
                    context=row["context"],
                    importance=row["importance"],
                    timestamp=row["timestamp"],
                    tags=json.loads(row["tags"]) if row["tags"] else []
                )
                for row in rows
            ]
    
    def save_agent_profile(self, profile: AgentProfile) -> bool:
        """保存代理档案"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO agent_profiles
                       (agent_name, personality, created_at, total_interactions,
                        known_facts, learned_preferences, relationship_scores)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        profile.agent_name,
                        profile.personality,
                        profile.created_at,
                        profile.total_interactions,
                        json.dumps(profile.known_facts),
                        json.dumps(profile.learned_preferences),
                        json.dumps(profile.relationship_scores)
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"保存档案失败: {e}")
            return False
    
    def get_agent_profile(self, agent_name: str) -> Optional[AgentProfile]:
        """获取代理档案"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM agent_profiles WHERE agent_name = ?",
                (agent_name,)
            )
            row = cursor.fetchone()
            
            if row:
                return AgentProfile(
                    agent_name=row["agent_name"],
                    personality=row["personality"],
                    created_at=row["created_at"],
                    total_interactions=row["total_interactions"],
                    known_facts=json.loads(row["known_facts"]) if row["known_facts"] else [],
                    learned_preferences=json.loads(row["learned_preferences"]) if row["learned_preferences"] else {},
                    relationship_scores=json.loads(row["relationship_scores"]) if row["relationship_scores"] else {}
                )
            return None


class MemoryManager:
    """
    记忆管理器
    为AI代理提供记忆功能
    """
    
    def __init__(self, db_path: str = "memory/orchestra_memory.db"):
        self.store = MemoryStore(db_path)
        self.session_id = self._generate_session_id()
        self._ensure_session()
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]
        return f"{timestamp}_{random_str}"
    
    def _ensure_session(self):
        """确保会话记录存在"""
        with sqlite3.connect(self.store.db_path) as conn:
            conn.execute(
                """INSERT OR IGNORE INTO sessions 
                   (session_id, session_type, created_at, summary)
                   VALUES (?, ?, ?, ?)""",
                (self.session_id, "orchestra", datetime.now().isoformat(), "")
            )
            conn.commit()
    
    def remember(self, agent_name: str, content: str,
                 context: str = "", memory_type: str = "fact",
                 importance: int = 5, tags: List[str] = None) -> bool:
        """
        记录一条记忆
        
        Args:
            agent_name: AI代理名称
            content: 记忆内容
            context: 上下文
            memory_type: 记忆类型 (fact/opinion/event/preference)
            importance: 重要程度 1-10
            tags: 标签列表
        """
        entry = MemoryEntry(
            id=hashlib.md5(f"{agent_name}{content}{datetime.now()}".encode()).hexdigest(),
            agent_name=agent_name,
            session_id=self.session_id,
            memory_type=memory_type,
            content=content,
            context=context,
            importance=importance,
            timestamp=datetime.now().isoformat(),
            tags=tags or []
        )
        
        return self.store.save_memory(entry)
    
    def recall(self, agent_name: str, context: str = "",
               limit: int = 10, min_importance: int = 1) -> List[MemoryEntry]:
        """
        回忆相关记忆
        
        Args:
            agent_name: AI代理名称
            context: 当前上下文（用于搜索相关记忆）
            limit: 返回数量
            min_importance: 最小重要程度
        """
        memories = self.store.get_memories(
            agent_name=agent_name,
            min_importance=min_importance,
            limit=limit * 2
        )
        
        # 如果有上下文，尝试搜索相关内容
        if context:
            keywords = self._extract_keywords(context)
            for keyword in keywords:
                found = self.store.search_memories(keyword, limit=5)
                for mem in found:
                    if mem not in memories:
                        memories.append(mem)
        
        # 去重并按重要性排序
        seen = set()
        unique_memories = []
        for mem in memories:
            if mem.id not in seen:
                seen.add(mem.id)
                unique_memories.append(mem)
        
        return sorted(unique_memories, key=lambda x: x.importance, reverse=True)[:limit]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化版）"""
        # 简单的关键词提取，实际可以用NLP
        words = text.split()
        # 过滤短词，返回较长的词作为关键词
        return [w for w in words if len(w) >= 4][:5]
    
    def format_memories_for_prompt(self, memories: List[MemoryEntry]) -> str:
        """将记忆格式化为提示词"""
        if not memories:
            return ""
        
        lines = ["\n【你的记忆】"]
        for mem in memories:
            lines.append(f"- {mem.content}")
        
        return "\n".join(lines)
    
    def update_agent_profile(self, agent_name: str, personality: str,
                            interaction_delta: int = 1,
                            new_facts: List[str] = None,
                            preferences: Dict[str, Any] = None):
        """更新代理档案"""
        profile = self.store.get_agent_profile(agent_name)
        
        if profile is None:
            profile = AgentProfile(
                agent_name=agent_name,
                personality=personality,
                created_at=datetime.now().isoformat()
            )
        
        profile.total_interactions += interaction_delta
        
        if new_facts:
            profile.known_facts.extend(new_facts)
            profile.known_facts = list(set(profile.known_facts))  # 去重
        
        if preferences:
            profile.learned_preferences.update(preferences)
        
        self.store.save_agent_profile(profile)
        return profile
    
    def get_agent_context(self, agent_name: str) -> str:
        """获取代理的完整上下文（记忆+档案）"""
        profile = self.store.get_agent_profile(agent_name)
        memories = self.recall(agent_name, limit=5)
        
        context_parts = []
        
        if profile:
            context_parts.append(f"你是{agent_name}，性格{profile.personality}。")
            context_parts.append(f"你已经参与了{profile.total_interactions}次对话。")
            
            if profile.known_facts:
                context_parts.append("你知道的事实：" + "；".join(profile.known_facts[:5]))
        
        if memories:
            context_parts.append(self.format_memories_for_prompt(memories))
        
        return "\n".join(context_parts)
    
    def export_session_memory(self, session_id: Optional[str] = None) -> Dict:
        """导出会话记忆"""
        target_session = session_id or self.session_id
        
        memories = self.store.get_memories(session_id=target_session, limit=1000)
        
        return {
            "session_id": target_session,
            "exported_at": datetime.now().isoformat(),
            "memory_count": len(memories),
            "memories": [m.to_dict() for m in memories]
        }
    
    def import_session_memory(self, data: Dict) -> bool:
        """导入会话记忆"""
        try:
            for mem_data in data.get("memories", []):
                entry = MemoryEntry.from_dict(mem_data)
                self.store.save_memory(entry)
            return True
        except Exception as e:
            print(f"导入记忆失败: {e}")
            return False


# 记忆增强的AI代理包装器
class MemoryEnhancedAgent:
    """
    带记忆功能的AI代理包装器
    包装任何BaseAgent，为其添加记忆能力
    """
    
    def __init__(self, base_agent, memory_manager: MemoryManager):
        self.agent = base_agent
        self.memory = memory_manager
        self.agent_name = base_agent.name
        
        # 确保档案存在
        self.memory.update_agent_profile(
            self.agent_name,
            base_agent.personality.value if hasattr(base_agent, 'personality') else 'unknown'
        )
    
    async def generate(self, prompt: str, context: str = "") -> str:
        """
        生成回复（带记忆）
        """
        # 1. 获取相关记忆
        memories = self.memory.recall(self.agent_name, context, limit=5)
        memory_context = self.memory.format_memories_for_prompt(memories)
        
        # 2. 构建增强提示
        agent_context = self.memory.get_agent_context(self.agent_name)
        
        enhanced_prompt = f"""{agent_context}

{memory_context}

当前任务：
{prompt}"""
        
        # 3. 生成回复
        response = await self.agent.generate(enhanced_prompt)
        
        # 4. 记录这次交互
        self.memory.remember(
            agent_name=self.agent_name,
            content=f"回复: {response[:200]}",
            context=f"问题: {prompt[:100]}",
            memory_type="interaction",
            importance=3
        )
        
        # 5. 更新档案
        self.memory.update_agent_profile(
            self.agent_name,
            self.agent.personality.value if hasattr(self.agent, 'personality') else 'unknown',
            interaction_delta=1
        )
        
        return response


__all__ = [
    'MemoryManager',
    'MemoryStore',
    'MemoryEntry',
    'AgentProfile',
    'MemoryEnhancedAgent'
]
