#!/usr/bin/env python3
"""
AI-Orchestra 测试脚本
测试所有核心功能是否正常工作
"""

import asyncio
import sys

from core.base_agent import MockAgent, PersonalityType
from logic.orchestrator import HierarchyMode, CreativeWritingMode
from logic.werewolf_engine import WerewolfEngine, Role, GamePhase
from logic.script_kill_engine import ScriptKillEngine, ScriptGenre, GamePhase as SKPhase

print("=" * 60)
print("🎭 AI-Orchestra 功能测试")
print("=" * 60)

async def test_mock_agent():
    """测试模拟AI代理"""
    print("\n📌 测试1: MockAgent 模拟AI代理")
    print("-" * 40)
    
    for personality in PersonalityType:
        agent = MockAgent(f"Test-{personality.value}", personality)
        response = await agent.generate("量子纠缠是否支持超光速通信？")
        print(f"  [{personality.value:12}] {response[:50]}...")
    
    print("  ✅ MockAgent 测试通过")
    return True

async def test_hierarchy_mode():
    """测试三级决策模式"""
    print("\n📌 测试2: HierarchyMode 三级决策模式")
    print("-" * 40)
    
    # 创建学生、老师和校长
    students = [
        MockAgent("DeepSeek", PersonalityType.ANALYTICAL),
        MockAgent("豆包", PersonalityType.HUMOROUS),
        MockAgent("千问", PersonalityType.CAUTIOUS),
        MockAgent("元宝", PersonalityType.AGGRESSIVE),
        MockAgent("Kimi", PersonalityType.MEDIATOR),
        MockAgent("GPT-4", PersonalityType.ANALYTICAL)
    ]
    
    teachers = [
        MockAgent("Claude", PersonalityType.ANALYTICAL),
        MockAgent("千问-师", PersonalityType.CAUTIOUS),
        MockAgent("DeepSeek-师", PersonalityType.AGGRESSIVE)
    ]
    
    principal = MockAgent("Claude-校长", PersonalityType.MEDIATOR)
    
    hierarchy = HierarchyMode(students, teachers, principal)
    
    progress_logs = []
    def progress_callback(stage, message, data):
        progress_logs.append(f"  [{stage}] {message}")
    
    results = await hierarchy.execute("为什么天空是蓝色的？", progress_callback)
    
    for log in progress_logs[:6]:  # 只显示前6条
        print(log)
    print("  ...")
    
    assert "students" in results
    assert "teachers" in results
    assert "principal" in results
    print(f"  ✅ 三级决策完成，学生{len(results['students'])}人，老师{len(results['teachers'])}人")
    return True

async def test_creative_writing():
    """测试文学创作模式"""
    print("\n📌 测试3: CreativeWritingMode 文学创作模式")
    print("-" * 40)
    
    agents_pool = {f"agent_{i}": MockAgent(f"AI-{i}") for i in range(5)}
    creative = CreativeWritingMode(agents_pool)
    
    progress_logs = []
    def progress_callback(stage, message, data):
        progress_logs.append(f"  [{stage}] {message}")
    
    results = await creative.create_content(
        "web_novel",
        "重生之我在末世开超市",
        "爽文风格，节奏快",
        progress_callback
    )
    
    for log in progress_logs[:4]:
        print(log)
    
    assert "stages" in results
    assert "final_content" in results
    content_preview = results["final_content"][:60] if results["final_content"] else "无内容"
    print(f"  ✅ 创作完成，最终内容预览: {content_preview}...")
    return True

async def test_werewolf():
    """测试狼人杀游戏"""
    print("\n📌 测试4: WerewolfEngine 狼人杀游戏")
    print("-" * 40)
    
    game = WerewolfEngine(num_players=8)
    game.setup_game()
    
    print(f"  游戏初始化: {len(game.players)}人参与")
    print(f"  当前阶段: {game.current_phase.value}")
    print(f"  存活玩家: {len(game.alive_players)}")
    
    # 进行一轮游戏
    await game.play_round()
    
    print(f"  进行1轮后: 第{game.current_round}天，{game.current_phase.value}")
    print(f"  日志条目: {len(game.logs)}条")
    
    assert len(game.players) == 8
    print("  ✅ 狼人杀引擎测试通过")
    return True

async def test_script_kill():
    """测试剧本杀游戏"""
    print("\n📌 测试5: ScriptKillEngine 剧本杀")
    print("-" * 40)
    
    engine = ScriptKillEngine("ancient_mansion")
    setup = engine.setup_game()
    
    print(f"  剧本: {setup['script']['title']}")
    print(f"  类型: {setup['script']['genre']}")
    print(f"  参与人数: {len(setup['players'])}人")
    
    for player in setup['players'][:3]:
        print(f"    - {player['display_name']}")
    if len(setup['players']) > 3:
        print(f"    ... 还有{len(setup['players'])-3}人")
    
    # 测试搜证
    clue = await engine.search_clue("沈少爷", "书房")
    if clue:
        print(f"  搜证测试: 在书房发现「{clue.name}」")
    
    # 测试讨论
    response = await engine.discuss("沈少爷", "你觉得谁是凶手？")
    print(f"  讨论测试: 沈少爷发言完成")
    
    # 测试投票
    engine.vote("二姨太", "沈少爷")
    print(f"  投票测试: 二姨太投票完成")
    
    # 揭晓真相
    truth = engine.reveal_truth()
    print(f"  真相: 凶手是「{truth['murderer']}」")
    
    assert engine.script is not None
    print("  ✅ 剧本杀引擎测试通过")
    return True

async def run_all_tests():
    """运行所有测试"""
    print("\n开始测试...\n")
    
    tests = [
        ("MockAgent", test_mock_agent),
        ("三级决策", test_hierarchy_mode),
        ("文学创作", test_creative_writing),
        ("狼人杀", test_werewolf),
        ("剧本杀", test_script_kill),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
