# 🎭 AI-Orchestra 项目归档文档

**项目状态**: v0.2.0 - 完整版归档  
**归档日期**: 2026-03-13  
**项目位置**: `/root/.openclaw/workspace/AI-Orchestra/`  
**打包文件**: `AI-Orchestra-v0.2.0.tar.gz` (91KB)

---

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| 总代码行数 | 3,482 行 |
| Python 文件数 | 6 个核心模块 |
| 支持AI数量 | 10+ (DeepSeek/豆包/千问/元宝/Kimi/GPT-4/Claude等) |
| 工作模式 | 5 种 |
| 游戏剧本 | 2 个完整剧本杀剧本 |
| 性格类型 | 5 种 |
| 创作类型 | 4 种 (网络小说/小红书/公众号/电商) |

---

## 🗂️ 文件清单

```
AI-Orchestra/
├── config.yaml                 # API配置模板
├── requirements.txt            # 依赖清单
├── README.md                   # 项目说明
├── test_all.py                 # 测试脚本
│
├── core/
│   └── base_agent.py           # 448行 - AI代理基类
│       ├── BaseAgent (抽象基类)
│       ├── MockAgent (模拟模式)
│       ├── DeepSeekAgent
│       ├── DoubaoAgent
│       ├── QwenAgent
│       ├── YuanbaoAgent
│       ├── KimiAgent
│       ├── GPT4Agent
│       └── ClaudeAgent
│
├── logic/
│   ├── orchestrator.py         # 612行 - 调度中心
│   │   ├── HierarchyMode (三级决策)
│   │   └── CreativeWritingMode (文学创作)
│   │
│   ├── werewolf_engine.py      # 626行 - 狼人杀引擎
│   │   ├── WerewolfEngine (游戏主控)
│   │   ├── Player (玩家数据)
│   │   ├── Role (角色枚举)
│   │   ├── GamePhase (阶段枚举)
│   │   └── Team (阵营枚举)
│   │
│   ├── script_kill_engine.py   # 584行 - 剧本杀引擎 ⭐
│   │   ├── ScriptKillEngine (游戏主控)
│   │   ├── Script (剧本数据)
│   │   ├── RoleScript (角色剧本)
│   │   ├── Clue (线索)
│   │   ├── MurderScript (凶案)
│   │   └── SCRIPTS_LIBRARY (剧本库)
│   │
│   └── memory_system.py        # 584行 - 对话记忆系统 ⭐
│       ├── MemoryManager (记忆管理)
│       ├── MemoryStore (存储层)
│       ├── MemoryEntry (记忆条目)
│       ├── AgentProfile (代理档案)
│       └── MemoryEnhancedAgent (记忆增强代理)
│
├── ui/
│   └── app.py                  # 1,228行 - Streamlit界面
│
└── memory/                     # SQLite数据库目录
    └── orchestra_memory.db     # 自动生成
```

---

## ✅ 功能完成度

### 核心功能 (100%)

| 功能模块 | 完成度 | 说明 |
|---------|--------|------|
| 三级决策模式 | ✅ 100% | 6学生→3老师→1校长完整流程 |
| 文学创作模式 | ✅ 100% | 4种创作类型完整支持 |
| 狼人杀引擎 | ✅ 100% | 完整游戏流程含夜晚/白天 |
| 剧本杀引擎 | ✅ 100% | 2剧本完整流程 |
| 对话记忆系统 | ✅ 100% | SQLite持久化+Web管理 |
| AI性格系统 | ✅ 100% | 5种性格类型 |
| Streamlit界面 | ✅ 100% | 5种模式可视化 |
| 结果导出 | ✅ 100% | 所有模式支持导出 |
| 模拟模式 | ✅ 100% | 无API Key可测试 |

### 待开发功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 真实API接入 | P1 | 配置Key后启用真实AI |
| 更多剧本 | P2 | 可增加更多剧本杀剧本 |
| 游戏回放 | P3 | 狼人杀/剧本杀回放功能 |
| 更多创作类型 | P3 | 短视频脚本、广告文案 |

---

## 🎭 剧本杀剧本详情

### 剧本1: 古宅迷踪
- **类型**: 古风悬疑
- **人数**: 6人
- **难度**: ⭐⭐⭐
- **背景**: 清朝末年江南首富沈家大院，沈老爷六十大寿当夜被杀
- **角色**: 沈少爷(凶手)、二姨太、管家、赵掌柜、李大夫、小翠
- **线索**: 9条线索分布在书房、花园、厨房、客房、下人房
- **真相**: 沈少爷为继承家产、摆脱控制而弑父

### 剧本2: 办公室疑云
- **类型**: 现代推理
- **人数**: 5人
- **难度**: ⭐⭐
- **背景**: 互联网公司CEO张明被发现死在办公室
- **角色**: CTO(凶手)、CFO、HR、销售总监、产品经理
- **线索**: 6条线索分布在办公室、CTO办公室、财务室等
- **真相**: CTO因股权纠纷杀人

---

## 🧠 记忆系统功能

### 记忆类型
- `fact` - 事实记忆
- `opinion` - 观点记忆
- `event` - 事件记忆
- `preference` - 偏好记忆
- `interaction` - 交互记忆

### 管理功能
- 记忆浏览（按代理/类型/重要度筛选）
- 关键词搜索
- 代理档案查看
- JSON导入/导出
- 数据清理

### 数据结构
```python
MemoryEntry:
  - id: 唯一标识
  - agent_name: AI代理名称
  - session_id: 会话ID
  - memory_type: 记忆类型
  - content: 内容
  - context: 上下文
  - importance: 重要度(1-10)
  - timestamp: 时间戳
  - tags: 标签列表
```

---

## 🚀 使用方式

### 启动命令
```bash
cd AI-Orchestra
pip install -r requirements.txt --break-system-packages
streamlit run ui/app.py
```

### 访问地址
- Web界面: http://localhost:8501

### 配置真实API
编辑 `config.yaml`:
```yaml
api_keys:
  deepseek:
    api_key: "your-api-key"
    base_url: "https://api.deepseek.com/v1"
    model: "deepseek-chat"
  # 其他AI配置...
```

---

## 📦 打包文件

| 文件名 | 大小 | 说明 |
|--------|------|------|
| AI-Orchestra-v0.2.0.tar.gz | 91KB | 最新完整版 (推荐) |
| AI-Orchestra-v0.1.0.tar.gz | 23KB | 旧版Beta |

---

## 🔄 版本历史

### v0.2.0 (2026-03-13)
- ✅ 新增剧本杀引擎（2个完整剧本）
- ✅ 新增对话记忆系统
- ✅ 优化Web界面（5种模式）
- ✅ 项目归档

### v0.1.0 (2026-03-13)
- ✅ 三级决策模式
- ✅ 文学创作模式
- ✅ 狼人杀引擎
- ✅ Streamlit界面

---

## 💡 后续开发建议

### 短期 (1-2周)
1. 配置真实API Key，测试真实AI响应
2. 增加2-3个新剧本杀剧本
3. 优化记忆系统的上下文关联

### 中期 (1月)
1. 增加更多创作类型（短视频脚本、广告文案）
2. 实现游戏回放功能
3. 添加AI代理之间的关系网络图

### 长期
1. 支持自定义剧本创作
2. 多语言支持
3. API接口开放

---

## 📝 技术债务

| 问题 | 严重程度 | 建议 |
|------|----------|------|
| 模拟模式回复较简单 | 低 | 可增加更多模板 |
| 无单元测试 | 中 | 添加pytest测试 |
| 配置文件敏感信息 | 低 | 支持环境变量 |
| 无日志系统 | 低 | 添加logging模块 |

---

## 🔗 相关文档

- MEMORY.md - 项目记忆存档
- AI-Orchestra-v0.2.0-发布说明.md - 发布说明
- X402_开发总结报告.md - 其他项目参考

---

**归档完成** | 准备开始下一个项目
