"""
AI-Orchestra: Streamlit Web界面
Mac用户可以直接运行: streamlit run ui/app.py
"""

import streamlit as st
import asyncio
from datetime import datetime

from core.base_agent import MockAgent, PersonalityType, create_agent
from logic.orchestrator import HierarchyMode, CreativeWritingMode
from logic.werewolf_engine import WerewolfEngine, Role, GamePhase, Team
from logic.script_kill_engine import ScriptKillEngine, ScriptGenre, Script, SCRIPTS_LIBRARY
from logic.memory_system import MemoryManager, MemoryEnhancedAgent


def run_sync(coro):
    """同步运行异步协程的辅助函数"""
    return asyncio.run(coro)

# 页面配置
st.set_page_config(
    page_title="AI-Orchestra | 多AI协作引擎",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #666;
    margin-bottom: 2rem;
}
.agent-card {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    border-left: 4px solid #667eea;
}
.personality-aggressive { border-left-color: #e74c3c; }
.personality-cautious { border-left-color: #3498db; }
.personality-humorous { border-left-color: #f39c12; }
.personality-analytical { border-left-color: #2ecc71; }
.personality-mediator { border-left-color: #9b59b6; }
.stage-badge {
    background: #667eea;
    color: white;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 0.8rem;
    margin-right: 5px;
}
</style>
""", unsafe_allow_html=True)

# 侧边栏导航
with st.sidebar:
    st.markdown("## 🎭 AI-Orchestra")
    st.markdown("*多AI协作智能引擎*")
    st.divider()
    
    mode = st.radio(
        "选择模式",
        ["三级决策模式", "文学创作模式", "AI大乱斗(狼人杀)", "剧本杀", "记忆系统", "系统状态"],
        index=0
    )
    
    st.divider()
    st.markdown("### 系统状态")
    st.info("🟢 模拟模式运行中\n\n(无API Key，使用模拟AI)")
    
    st.markdown("### 支持的AI")
    ai_list = ["DeepSeek", "豆包", "通义千问", "元宝", "Kimi", "GPT-4", "Claude"]
    for ai in ai_list:
        st.markdown(f"- {ai}")

# 主内容区
st.markdown('<p class="main-header">🎭 AI-Orchestra</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">让多个AI协作，获得更靠谱的答案</p>', unsafe_allow_html=True)

# ==================== 三级决策模式 ====================
if mode == "三级决策模式":
    st.header("三级决策模式")
    st.markdown("6个学生AI回答 → 3个老师AI评判 → 1个校长AI决策")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        question = st.text_area(
            "输入你的问题",
            placeholder="例如：量子纠缠是否支持超光速通信？为什么？",
            height=100
        )
    
    with col2:
        st.markdown("### 角色配置")
        st.markdown("**学生组 (6人)**")
        st.markdown("DeepSeek, 豆包, 千问, 元宝, Kimi, GPT-4")
        st.markdown("**老师组 (3人)**")
        st.markdown("Claude, 千问, DeepSeek")
        st.markdown("**校长 (1人)**")
        st.markdown("Claude")
    
    if st.button("🚀 启动协作分析", type="primary", disabled=not question):
        with st.spinner("正在协调10个AI进行协作..."):
            # 创建代理
            students = [
                MockAgent("DeepSeek", PersonalityType.ANALYTICAL),
                MockAgent("豆包", PersonalityType.HUMOROUS),
                MockAgent("通义千问", PersonalityType.CAUTIOUS),
                MockAgent("元宝", PersonalityType.AGGRESSIVE),
                MockAgent("Kimi", PersonalityType.MEDIATOR),
                MockAgent("GPT-4", PersonalityType.ANALYTICAL)
            ]
            
            teachers = [
                MockAgent("Claude", PersonalityType.ANALYTICAL),
                MockAgent("千问(师)", PersonalityType.CAUTIOUS),
                MockAgent("DeepSeek(师)", PersonalityType.AGGRESSIVE)
            ]
            
            principal = MockAgent("Claude(校长)", PersonalityType.MEDIATOR)
            
            # 创建模式实例
            hierarchy = HierarchyMode(students, teachers, principal)
            
            # 进度容器
            progress_container = st.container()
            
            def progress_callback(stage, message, data):
                with progress_container:
                    if "stage1" in stage:
                        st.markdown(f"<span class='stage-badge'>阶段1</span> {message}", unsafe_allow_html=True)
                    elif "stage2" in stage:
                        st.markdown(f"<span class='stage-badge'>阶段2</span> {message}", unsafe_allow_html=True)
                    elif "stage3" in stage:
                        st.markdown(f"<span class='stage-badge'>阶段3</span> {message}", unsafe_allow_html=True)
                    elif stage == "complete":
                        st.success("✅ 协作完成！")
            
            # 运行
            results = run_sync(
                hierarchy.execute(question, progress_callback)
            )
            
            # 显示结果
            st.divider()
            
            # 学生回答
            st.subheader("📚 学生组回答")
            student_cols = st.columns(2)
            for i, (name, data) in enumerate(results["students"].items()):
                with student_cols[i % 2]:
                    personality_class = f"personality-{data['personality']}"
                    st.markdown(f"""
                    <div class="agent-card {personality_class}">
                        <strong>🎓 {name}</strong> 
                        <span style="color: #999; font-size: 0.8rem;">({data['personality']})</span><br/>
                        {data['answer'][:300]}...
                    </div>
                    """, unsafe_allow_html=True)
            
            # 老师评判
            st.subheader("👨‍🏫 老师组评判")
            for name, data in results["teachers"].items():
                personality_class = f"personality-{data['personality']}"
                st.markdown(f"""
                <div class="agent-card {personality_class}">
                    <strong>👨‍🏫 {name}</strong>
                    <span style="color: #999; font-size: 0.8rem;">({data['personality']})</span><br/>
                    {data['evaluation'][:400]}...
                </div>
                """, unsafe_allow_html=True)
            
            # 校长决策
            st.subheader("👑 校长最终决策")
            principal_data = results["principal"]
            st.markdown(f"""
            <div class="agent-card personality-mediator" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <strong>👑 {principal_data['agent_name']} (校长)</strong><br/><br/>
                {principal_data['answer']}
            </div>
            """, unsafe_allow_html=True)
            
            # 导出按钮
            st.divider()
            result_text = f"""
问题：{question}

=== 学生回答 ===
"""
            for name, data in results["students"].items():
                result_text += f"\n【{name}】\n{data['answer']}\n"
            
            result_text += "\n=== 老师评判 ===\n"
            for name, data in results["teachers"].items():
                result_text += f"\n【{name}】\n{data['evaluation']}\n"
            
            result_text += f"\n=== 校长决策 ===\n\n{principal_data['answer']}\n"
            
            st.download_button(
                "📥 导出完整报告",
                result_text,
                file_name=f"ai_orchestra_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# ==================== 文学创作模式 ====================
elif mode == "文学创作模式":
    st.header("📝 AI协作文学创作")
    st.markdown("多个AI协作完成创作：大纲→情节→润色→审核")
    
    content_type = st.selectbox(
        "选择创作类型",
        ["网络小说", "小红书文案", "公众号文章", "电商文案"],
        index=0
    )
    
    type_map = {
        "网络小说": "web_novel",
        "小红书文案": "xiaohongshu",
        "公众号文章": "wechat",
        "电商文案": "ecommerce"
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("主题/标题", placeholder="例如：重生之我在末世开超市")
        requirements = st.text_area("特殊要求（可选）", placeholder="例如：爽文风格，主角有空间异能，节奏要快...", height=80)
    
    with col2:
        st.markdown("### 创作流程")
        if content_type == "网络小说":
            st.markdown("1. 📋 大纲规划师")
            st.markdown("2. ✍️ 情节写手")
            st.markdown("3. 💬 对话润色师")
            st.markdown("4. 👨‍💼 主编审核")
        elif content_type == "小红书文案":
            st.markdown("1. 🎯 标题专家")
            st.markdown("2. 📝 内容创作者")
            st.markdown("3. 🏷️ 标签专家")
        elif content_type == "公众号文章":
            st.markdown("1. 🎯 标题创作")
            st.markdown("2. 📝 引言写作")
            st.markdown("3. 📄 正文创作")
            st.markdown("4. ✨ 结尾升华")
            st.markdown("5. 📐 排版优化")
        elif content_type == "电商文案":
            st.markdown("1. 🔍 市场调研")
            st.markdown("2. ✍️ 文案创作")
    
    if st.button("🚀 开始创作", type="primary", disabled=not topic):
        with st.spinner("AI团队正在协作创作..."):
            # 创建创作模式实例
            agents_pool = {f"agent_{i}": MockAgent(f"AI-{i}") for i in range(5)}
            creative = CreativeWritingMode(agents_pool)
            
            # 进度容器
            progress_placeholder = st.empty()
            
            def progress_callback(stage, message, data):
                progress_placeholder.info(f"⏳ {message}")
            
            # 运行创作
            results = run_sync(
                creative.create_content(
                    type_map[content_type],
                    topic,
                    requirements,
                    progress_callback
                )
            )
            
            progress_placeholder.empty()
            
            # 显示各阶段结果
            st.divider()
            st.subheader("🎨 创作过程")
            
            for stage_name, stage_data in results["stages"].items():
                with st.expander(f"📌 {stage_name} - {stage_data['agent']}"):
                    st.markdown(stage_data['content'])
            
            # 最终内容
            st.divider()
            st.subheader("✨ 最终作品")
            st.markdown("---")
            st.markdown(results["final_content"])
            st.markdown("---")
            
            # 导出
            st.download_button(
                "📥 导出完整作品",
                results["final_content"],
                file_name=f"ai_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# ==================== AI大乱斗(狼人杀) ====================
elif mode == "AI大乱斗(狼人杀)":
    st.header("🐺 AI大乱斗 - 狼人杀")
    st.markdown("10个性格各异的AI进行狼人杀对决！")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("游戏配置")
        num_players = st.slider("玩家人数", 6, 12, 10)
        max_rounds = st.slider("最大回合数", 5, 30, 20)
        
        st.markdown("### 角色分配")
        roles_count = {
            "🐺 狼人": 2,
            "👤 平民": num_players - 5,
            "🔮 预言家": 1,
            "🧙 女巫": 1,
            "🔫 猎人": 1
        }
        
        for role, count in roles_count.items():
            st.markdown(f"- {role}: {count}人")
    
    with col2:
        st.subheader("性格配置")
        st.markdown("每位AI将随机获得一种性格：")
        
        personalities = {
            "🔴 激进型": "喜欢反驳，逻辑硬核",
            "🔵 谨慎型": "说话滴水不漏",
            "🟡 幽默型": "爱说烂梗",
            "🟢 学霸型": "列提纲引用数据",
            "🟣 和事佬": "倾向平衡各方"
        }
        
        for p, desc in personalities.items():
            st.markdown(f"{p}: {desc}")
    
    # 游戏控制
    if 'werewolf_game' not in st.session_state:
        st.session_state.werewolf_game = None
        st.session_state.game_started = False
    
    col_start, col_next, col_reset = st.columns(3)
    
    with col_start:
        if st.button("🎮 开始新游戏", type="primary"):
            st.session_state.werewolf_game = WerewolfEngine(num_players=num_players)
            st.session_state.game_started = True
            st.session_state.game_result = None
            
            # 初始化游戏
            st.session_state.werewolf_game.setup_game()
            st.rerun()
    
    with col_next:
        if st.session_state.game_started and st.session_state.werewolf_game:
            if not st.session_state.werewolf_game.game_over:
                if st.button("⏭️ 进行下一轮", type="secondary"):
                    with st.spinner("AI正在思考和行动..."):
                        run_sync(
                            st.session_state.werewolf_game.play_round()
                        )
                    st.rerun()
    
    with col_reset:
        if st.session_state.game_started:
            if st.button("🔄 重置游戏"):
                st.session_state.werewolf_game = None
                st.session_state.game_started = False
                st.session_state.game_result = None
                st.rerun()
    
    # 显示游戏状态
    if st.session_state.game_started and st.session_state.werewolf_game:
        game = st.session_state.werewolf_game
        
        st.divider()
        
        # 游戏状态概览
        status_cols = st.columns(4)
        with status_cols[0]:
            st.metric("当前天数", f"第{game.current_round}天")
        with status_cols[1]:
            st.metric("存活人数", len(game.alive_players))
        with status_cols[2]:
            st.metric("死亡人数", len(game.dead_players))
        with status_cols[3]:
            phase_display = game.current_phase.value if game.current_round > 0 else "准备阶段"
            st.metric("当前阶段", phase_display)
        
        # 玩家状态
        st.subheader("🎲 玩家状态")
        
        player_cols = st.columns(3)
        for i, (pid, player) in enumerate(game.players.items()):
            with player_cols[i % 3]:
                # 身份图标
                role_emoji = {
                    Role.WEREWOLF: "🐺",
                    Role.VILLAGER: "👤",
                    Role.PROPHET: "🔮",
                    Role.WITCH: "🧙",
                    Role.HUNTER: "🔫"
                }.get(player.role, "👤")
                
                # 存活状态
                status = "🟢 存活" if player.is_alive else "🔴 死亡"
                
                # 身份显示（死亡后显示真实身份）
                role_display = player.role.value if (not player.is_alive or player.is_revealed) else "???"
                
                personality_class = f"personality-{player.personality.value}"
                
                st.markdown(f"""
                <div class="agent-card {personality_class}" style="{'opacity: 0.6;' if not player.is_alive else ''}">
                    {role_emoji} <strong>{player.name}</strong> 
                    <span style="float: right;">{status}</span><br/>
                    身份: {role_display} | 性格: {player.personality.value}
                </div>
                """, unsafe_allow_html=True)
        
        # 游戏日志
        st.subheader("📜 游戏记录")
        
        # 显示最近的游戏日志
        recent_logs = game.logs[-20:] if len(game.logs) > 20 else game.logs
        log_text = "\n".join([f"[第{log.round}天 - {log.phase}] {log.content}" for log in recent_logs])
        st.text_area("最近记录", log_text, height=300, label_visibility="collapsed")
        
        # 游戏结束显示
        if game.game_over:
            st.divider()
            winner_emoji = "🐺" if game.winner == Team.EVIL else "👥"
            st.balloons()
            st.success(f"{winner_emoji} 游戏结束！{game.winner.value} 胜利！")
            
            # 导出完整记录
            full_logs = game.get_full_logs()
            st.download_button(
                "📥 导出完整游戏记录",
                full_logs,
                file_name=f"werewolf_game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# ==================== 剧本杀模式 ====================
elif mode == "剧本杀":
    st.header("📖 AI剧本杀")
    st.markdown("扮演角色，收集线索，找出真凶！")
    
    # 剧本选择
    st.subheader("选择剧本")
    
    script_options = {
        "古宅迷踪": "ancient_mansion",
        "办公室疑云": "modern_office"
    }
    
    selected_script_name = st.selectbox(
        "选择剧本",
        list(script_options.keys()),
        index=0
    )
    
    selected_script_id = script_options[selected_script_name]
    script_info = SCRIPTS_LIBRARY[selected_script_id]
    
    # 显示剧本信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("类型", script_info.genre.value)
    with col2:
        st.metric("难度", "⭐" * script_info.difficulty)
    with col3:
        st.metric("人数", f"{script_info.player_count}人")
    
    with st.expander("📜 剧本背景"):
        st.markdown(script_info.background_story)
    
    # 游戏控制
    if 'script_kill_game' not in st.session_state:
        st.session_state.script_kill_game = None
        st.session_state.script_game_started = False
        st.session_state.player_role = None
        st.session_state.current_view = "intro"
    
    col_start, col_reset = st.columns(2)
    
    with col_start:
        if st.button("🎭 开始游戏", type="primary"):
            st.session_state.script_kill_game = ScriptKillEngine(selected_script_id)
            setup_result = st.session_state.script_kill_game.setup_game()
            st.session_state.script_game_started = True
            st.session_state.setup_result = setup_result
            
            # 为当前用户分配一个角色（简化：第一个角色）
            if setup_result["players"]:
                st.session_state.player_role = setup_result["players"][0]["role"]
                st.session_state.player_display_name = setup_result["players"][0]["display_name"]
            
            st.rerun()
    
    with col_reset:
        if st.session_state.script_game_started:
            if st.button("🔄 重置"):
                st.session_state.script_kill_game = None
                st.session_state.script_game_started = False
                st.session_state.player_role = None
                st.rerun()
    
    # 游戏进行
    if st.session_state.script_game_started and st.session_state.script_kill_game:
        engine = st.session_state.script_kill_game
        
        st.divider()
        
        # 导航标签
        tabs = st.tabs(["🎭 我的角色", "🔍 线索搜集", "💬 讨论", "🗳️ 投票", "📜 真相"])
        
        # Tab 1: 我的角色
        with tabs[0]:
            if st.session_state.player_role:
                role_script = engine.get_role_script(st.session_state.player_role)
                
                st.subheader(f"你的身份：{role_script.display_name}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📖 背景故事")
                    st.markdown(role_script.background)
                    
                    st.markdown("### 🎯 你的目标")
                    for goal in role_script.goals:
                        st.markdown(f"- {goal}")
                
                with col2:
                    with st.expander("🔒 秘密（不要让别人知道！）", expanded=True):
                        for secret in role_script.secrets:
                            st.markdown(f"- 🔴 {secret}")
                    
                    st.markdown("### 📢 公开信息")
                    st.info(role_script.public_info)
                    
                    if role_script.alibi:
                        st.markdown("### 🕐 不在场证明")
                        st.success(role_script.alibi)
        
        # Tab 2: 线索搜集
        with tabs[1]:
            st.subheader("🔍 搜集线索")
            
            # 可搜证地点
            locations = list(set([clue.location for clue in engine.script.clues.values()]))
            
            st.markdown("### 选择搜证地点")
            cols = st.columns(3)
            for i, location in enumerate(locations):
                with cols[i % 3]:
                    if st.button(f"📍 {location}", key=f"loc_{location}"):
                        with st.spinner(f"正在{location}搜索..."):
                            clue = run_sync(
                                engine.search_clue(st.session_state.player_role, location)
                            )
                            if clue:
                                st.success(f"发现线索：{clue.name}")
                            else:
                                st.info(f"在{location}没有发现新线索")
            
            # 已发现线索
            st.markdown("### 📋 已发现线索")
            if engine.discovered_clues:
                for clue_id, clue in engine.discovered_clues.items():
                    with st.expander(f"{clue.name} ({clue.location})"):
                        st.markdown(clue.description)
                        st.caption(f"发现者：{clue.discovered_by}")
            else:
                st.info("还没有发现任何线索，快去搜证吧！")
        
        # Tab 3: 讨论
        with tabs[2]:
            st.subheader("💬 讨论发言")
            
            # 简化版讨论：选择一个话题，AI回复
            topics = [
                "你觉得谁是凶手？",
                "你在案发时在哪里？",
                "你对死者的看法？",
                "你有什么可疑的发现？"
            ]
            
            selected_topic = st.selectbox("选择话题", topics)
            
            if st.button("🎤 发言"):
                with st.spinner("AI正在思考..."):
                    # 每个角色发言
                    for role_name, agent in list(engine.players.items())[:4]:  # 限制显示4个
                        response = run_sync(
                            engine.discuss(role_name, selected_topic)
                        )
                        
                        role_script = engine.script.roles[role_name]
                        st.markdown(f"**{role_script.display_name}**：{response}")
                        st.divider()
        
        # Tab 4: 投票
        with tabs[3]:
            st.subheader("🗳️ 指认凶手")
            
            # 嫌疑人列表
            suspects = [(role, script.display_name) for role, script in engine.script.roles.items()]
            
            suspect_options = {display: role for role, display in suspects}
            selected_suspect = st.selectbox("你选择指认谁？", list(suspect_options.keys()))
            
            if st.button("✅ 提交投票"):
                result = engine.vote(st.session_state.player_role, suspect_options[selected_suspect])
                
                if result:
                    st.success("所有人都已投票！")
                    vote_result = engine.get_vote_result()
                    
                    st.divider()
                    st.subheader("📊 投票结果")
                    
                    if vote_result["is_correct"]:
                        st.balloons()
                        st.success(f"🎉 指认正确！凶手确实是 {vote_result['real_murderer']}")
                    else:
                        st.error(f"❌ 指认错误！真凶是 {vote_result['real_murderer']}")
                    
                    st.markdown(f"### 结局\n{vote_result['ending']}")
                else:
                    st.info("投票已提交，等待其他玩家...")
        
        # Tab 5: 真相
        with tabs[4]:
            st.subheader("📜 真相揭晓")
            
            if st.button("🔓 查看完整真相"):
                truth = engine.reveal_truth()
                
                st.markdown(f"### 受害者\n{truth['victim']}")
                st.markdown(f"### 真凶\n🐺 **{truth['murderer']}**")
                st.markdown(f"### 作案手法\n{truth['method']}")
                st.markdown(f"### 作案时间\n{truth['time']}")
                st.markdown(f"### 作案地点\n{truth['location']}")
                st.markdown(f"### 动机\n{truth['motive']}")
                
                st.markdown("### 关键证据")
                for evidence in truth['key_evidence']:
                    st.markdown(f"- {evidence}")
                
                st.markdown("### 案发时间线")
                for event in truth['timeline']:
                    st.markdown(f"- {event}")
            
            # 导出游戏记录
            if engine.game_log:
                if st.download_button(
                    "📥 导出游戏记录",
                    engine.get_game_summary(),
                    file_name=f"script_kill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                ):
                    pass

# ==================== 记忆系统 ====================
elif mode == "记忆系统":
    st.header("🧠 AI记忆系统")
    st.markdown("查看和管理AI的记忆与交互历史")
    
    # 初始化记忆管理器
    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = MemoryManager()
    
    memory = st.session_state.memory_manager
    
    # 标签页
    tabs = st.tabs(["💭 记忆浏览", "🔍 记忆搜索", "👤 代理档案", "⚙️ 系统管理"])
    
    # Tab 1: 记忆浏览
    with tabs[0]:
        st.subheader("AI记忆库")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            agent_filter = st.selectbox(
                "选择AI代理",
                ["全部", "DeepSeek", "豆包", "通义千问", "元宝", "Kimi", "GPT-4", "Claude"]
            )
        with col2:
            type_filter = st.selectbox(
                "记忆类型",
                ["全部", "fact", "opinion", "event", "preference", "interaction"]
            )
        with col3:
            min_importance = st.slider("最小重要度", 1, 10, 1)
        
        # 获取记忆
        agent_name = None if agent_filter == "全部" else agent_filter
        memory_type = None if type_filter == "全部" else type_filter
        
        memories = memory.store.get_memories(
            agent_name=agent_name,
            memory_type=memory_type,
            min_importance=min_importance,
            limit=50
        )
        
        st.markdown(f"**共找到 {len(memories)} 条记忆**")
        
        for mem in memories[:20]:  # 只显示前20条
            with st.expander(f"📝 {mem.agent_name} - {mem.memory_type} (重要度:{mem.importance})"):
                st.markdown(f"**内容：** {mem.content}")
                if mem.context:
                    st.markdown(f"**上下文：** {mem.context}")
                st.caption(f"时间：{mem.timestamp} | 标签：{', '.join(mem.tags) if mem.tags else '无'}")
    
    # Tab 2: 记忆搜索
    with tabs[1]:
        st.subheader("搜索记忆")
        
        search_query = st.text_input("输入关键词搜索", placeholder="例如：量子、狼人、创作...")
        
        if search_query:
            results = memory.store.search_memories(search_query, limit=20)
            
            st.markdown(f"**找到 {len(results)} 条相关记忆**")
            
            for mem in results:
                with st.expander(f"🔍 {mem.agent_name}: {mem.content[:50]}..."):
                    st.markdown(f"**完整内容：** {mem.content}")
                    if mem.context:
                        st.markdown(f"**上下文：** {mem.context}")
                    st.caption(f"类型：{mem.memory_type} | 重要度：{mem.importance} | 时间：{mem.timestamp}")
    
    # Tab 3: 代理档案
    with tabs[2]:
        st.subheader("AI代理档案")
        
        selected_agent = st.selectbox(
            "选择要查看的代理",
            ["DeepSeek", "豆包", "通义千问", "元宝", "Kimi", "GPT-4", "Claude"]
        )
        
        profile = memory.store.get_agent_profile(selected_agent)
        
        if profile:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("总交互次数", profile.total_interactions)
                st.markdown(f"**性格类型：** {profile.personality}")
                st.markdown(f"**创建时间：** {profile.created_at}")
            
            with col2:
                st.markdown("**已知事实：**")
                for fact in profile.known_facts[:10]:
                    st.markdown(f"- {fact}")
                
                if profile.learned_preferences:
                    st.markdown("**学习到的偏好：**")
                    for k, v in profile.learned_preferences.items():
                        st.markdown(f"- {k}: {v}")
        else:
            st.info(f"{selected_agent} 还没有档案记录。参与对话后将自动创建。")
    
    # Tab 4: 系统管理
    with tabs[3]:
        st.subheader("系统管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📤 导出记忆")
            if st.button("导出当前会话记忆"):
                export_data = memory.export_session_memory()
                st.download_button(
                    "下载JSON",
                    json.dumps(export_data, ensure_ascii=False, indent=2),
                    file_name=f"memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            st.markdown("### 📥 导入记忆")
            uploaded_file = st.file_uploader("选择记忆文件", type=["json"])
            if uploaded_file is not None:
                try:
                    import_data = json.load(uploaded_file)
                    if memory.import_session_memory(import_data):
                        st.success("记忆导入成功！")
                    else:
                        st.error("记忆导入失败")
                except Exception as e:
                    st.error(f"文件解析失败: {e}")
        
        st.divider()
        
        st.markdown("### 🧹 清理数据")
        if st.button("⚠️ 清除所有记忆", type="secondary"):
            st.warning("此操作不可恢复！")
            confirm = st.checkbox("确认删除所有记忆数据")
            if confirm:
                # 删除数据库文件
                db_path = memory.store.db_path
                if db_path.exists():
                    db_path.unlink()
                    st.session_state.memory_manager = MemoryManager()
                    st.success("所有记忆已清除")
                    st.rerun()

# ==================== 系统状态 ====================
elif mode == "系统状态":
    st.header("📊 系统状态")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("支持AI数量", "10+")
    with col2:
        st.metric("工作模式", "5种")
    with col3:
        st.metric("运行模式", "模拟模式")
    
    st.divider()
    
    st.subheader("🎭 AI角色库")
    
    ai_data = [
        ("DeepSeek", "学生/老师", "Analytical"),
        ("豆包", "学生", "Humorous"),
        ("通义千问", "学生/老师", "Cautious"),
        ("元宝", "学生", "Aggressive"),
        ("Kimi", "学生", "Mediator"),
        ("GPT-4", "学生", "Analytical"),
        ("Claude", "老师/校长", "Analytical/Mediator")
    ]
    
    for name, roles, personality in ai_data:
        st.markdown(f"- **{name}**: {roles} | 性格: {personality}")
    
    st.divider()
    
    st.subheader("📁 项目文件")
    st.markdown("""
    ```
    AI-Orchestra/
    ├── config.yaml          # 配置文件
    ├── core/
    │   └── base_agent.py    # AI代理基类
    ├── logic/
    │   ├── orchestrator.py  # 调度中心
    │   ├── werewolf_engine.py # 狼人杀引擎
    │   ├── script_kill_engine.py # 剧本杀引擎
    │   └── memory_system.py   # 对话记忆系统
    ├── memory/              # 记忆数据库
    ├── ui/
    │   └── app.py           # 本界面
    └── logs/                # 日志目录
    ```
    """)
    
    st.divider()
    
    st.subheader("🔧 配置API Key")
    st.markdown("编辑 `config.yaml` 文件，填入你的API Key即可切换到真实AI模式：")
    st.code("""
api_keys:
  deepseek:
    api_key: "your-api-key-here"
    base_url: "https://api.deepseek.com/v1"
    model: "deepseek-chat"
    """, language="yaml")

# 页脚
st.divider()
st.markdown("<p style='text-align: center; color: #999;'>AI-Orchestra v0.2.1 | 多AI协作引擎</p>", unsafe_allow_html=True)
