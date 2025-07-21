#!/usr/bin/env python3
"""
演示从 Agent Zero 项目获得的启发
展示增强的工具管理和通信系统
"""

import asyncio
from python.agent.enhanced_tool_manager import enhanced_tool_manager, Instrument
from python.agent.enhanced_communication import enhanced_communication, CommunicationEvent
from python.agent.core import Agent

async def demo_agent_zero_inspiration():
    """演示从 Agent Zero 获得的启发"""
    print("🛡️ Aegis Agent - Agent Zero 启发演示")
    print("=" * 60)
    
    # 1. 演示自定义函数工具 (Instruments)
    print("🔧 1. 自定义函数工具演示")
    print("-" * 40)
    
    # 创建自定义函数
    def calculate_fibonacci(n: int) -> int:
        """计算斐波那契数列"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    async def async_weather_check(city: str) -> str:
        """模拟天气查询"""
        await asyncio.sleep(0.1)  # 模拟网络请求
        return f"天气晴朗，温度25°C，城市: {city}"
    
    # 注册自定义函数工具
    enhanced_tool_manager.register_instrument(
        "fibonacci", 
        calculate_fibonacci, 
        "计算斐波那契数列"
    )
    
    enhanced_tool_manager.register_instrument(
        "weather", 
        async_weather_check, 
        "查询天气信息"
    )
    
    print(f"已注册自定义工具: {list(enhanced_tool_manager.instruments.keys())}")
    
    # 测试自定义工具
    fib_tool = enhanced_tool_manager.get_tool_instance("fibonacci")
    if fib_tool:
        result = await fib_tool.execute(n=10)
        print(f"斐波那契(10) = {result.data['result']}")
    
    weather_tool = enhanced_tool_manager.get_tool_instance("weather")
    if weather_tool:
        result = await weather_tool.execute(city="北京")
        print(f"天气查询: {result.data['result']}")
    
    print()
    
    # 2. 演示工具链
    print("⛓️ 2. 工具链演示")
    print("-" * 40)
    
    # 创建工具链
    enhanced_tool_manager.create_tool_chain(
        "data_analysis_chain",
        ["tavily_search", "code", "fibonacci"]
    )
    
    enhanced_tool_manager.create_tool_chain(
        "weather_chain",
        ["weather", "code"]
    )
    
    print("已创建工具链:")
    for chain_name, tools in enhanced_tool_manager.tool_chains.items():
        print(f"   ⛓️ {chain_name}: {' -> '.join(tools)}")
    
    print()
    
    # 3. 演示回退机制
    print("🔄 3. 回退机制演示")
    print("-" * 40)
    
    # 测试回退机制
    result = await enhanced_tool_manager.execute_with_fallback(
        "tavily_search",
        {"query": "Python教程"},
        fallback_tools=["search", "terminal"]
    )
    
    print(f"回退执行结果: {result.success}")
    if result.success:
        print(f"结果数据: {result.data}")
    else:
        print(f"错误信息: {result.error}")
    
    print()
    
    # 4. 演示增强通信系统
    print("📡 4. 增强通信系统演示")
    print("-" * 40)
    
    # 添加流式回调
    async def stream_callback(event: CommunicationEvent):
        print(f"📡 流式事件: {event.event_type} - {event.data}")
    
    enhanced_communication.add_stream_callback(stream_callback)
    
    # 测试流式通信
    await enhanced_communication.stream_message("开始执行任务", "info")
    await enhanced_communication.stream_progress("数据分析", 0.25, "正在收集数据")
    await enhanced_communication.stream_progress("数据分析", 0.5, "正在处理数据")
    await enhanced_communication.stream_progress("数据分析", 0.75, "正在生成报告")
    await enhanced_communication.stream_progress("数据分析", 1.0, "任务完成")
    await enhanced_communication.stream_message("任务执行完成", "success")
    
    print()
    
    # 5. 演示多智能体协作
    print("🤖 5. 多智能体协作演示")
    print("-" * 40)
    
    # 创建主智能体
    main_agent = Agent()
    
    # 创建子智能体
    search_agent = Agent()
    analysis_agent = Agent()
    
    # 设置层级关系
    search_agent.communication.set_superior(main_agent.communication)
    analysis_agent.communication.set_superior(main_agent.communication)
    
    print("智能体层级关系:")
    print(f"   主智能体: {main_agent.config.name}")
    print(f"   搜索智能体: {search_agent.config.name}")
    print(f"   分析智能体: {analysis_agent.config.name}")
    
    # 模拟协作任务
    await search_agent.communication.report_to_superior(
        "搜索任务完成", 
        {"query": "Python教程", "results": 5}
    )
    
    await analysis_agent.communication.report_to_superior(
        "分析任务完成", 
        {"analysis": "数据已处理", "insights": ["发现1", "发现2"]}
    )
    
    print()
    
    # 6. 演示工具统计
    print("📊 6. 工具统计演示")
    print("-" * 40)
    
    stats = enhanced_tool_manager.get_tool_statistics()
    print(f"总工具数: {stats['total_tools']}")
    print(f"自定义工具数: {stats['total_instruments']}")
    print(f"工具链数: {stats['total_chains']}")
    print(f"工具分类: {stats['tool_categories']}")
    
    print()
    
    # 7. 演示配置导出/导入
    print("💾 7. 配置导出/导入演示")
    print("-" * 40)
    
    # 导出工具配置
    tool_config = enhanced_tool_manager.export_tool_config()
    print(f"导出配置包含 {len(tool_config['tools'])} 个工具")
    print(f"导出配置包含 {len(tool_config['instruments'])} 个自定义工具")
    print(f"导出配置包含 {len(tool_config['chains'])} 个工具链")
    
    # 导出通信数据
    comm_data = await enhanced_communication.export_communication_data()
    print(f"导出通信数据包含 {len(comm_data['chat_history'])} 条历史记录")
    
    print()
    
    # 8. 演示系统摘要
    print("📋 8. 系统摘要演示")
    print("-" * 40)
    
    summary = enhanced_tool_manager.get_available_tools_summary()
    print(summary)
    
    comm_summary = enhanced_communication.get_communication_summary()
    print(f"通信摘要: {comm_summary}")

async def demo_web_ui_integration():
    """演示 Web UI 集成概念"""
    print("\n🌐 Web UI 集成概念演示")
    print("=" * 60)
    
    # 模拟 Web UI 事件处理
    class WebUI:
        def __init__(self):
            self.chat_messages = []
            self.tool_executions = []
            self.progress_updates = []
        
        async def handle_stream_event(self, event: CommunicationEvent):
            """处理流式事件"""
            if event.event_type == "stream":
                self.chat_messages.append({
                    "message": event.data["message"],
                    "type": event.data["type"],
                    "timestamp": event.timestamp.isoformat()
                })
                print(f"💬 新消息: {event.data['message']}")
            
            elif event.event_type == "progress":
                self.progress_updates.append({
                    "task": event.data["task"],
                    "progress": event.data["progress"],
                    "details": event.data["details"]
                })
                print(f"📈 进度更新: {event.data['task']} - {event.data['progress']*100:.0f}%")
            
            elif event.event_type == "tool_execution":
                self.tool_executions.append({
                    "tool": event.data["tool"],
                    "parameters": event.data["parameters"],
                    "result": event.data["result"]
                })
                print(f"🔧 工具执行: {event.data['tool']}")
    
    # 创建 Web UI 实例
    web_ui = WebUI()
    enhanced_communication.add_stream_callback(web_ui.handle_stream_event)
    
    # 模拟用户交互
    print("模拟用户交互...")
    await enhanced_communication.stream_message("用户: 请帮我分析Python项目", "user")
    await enhanced_communication.stream_message("系统: 开始分析Python项目", "system")
    await enhanced_communication.stream_progress("项目分析", 0.2, "扫描文件结构")
    await enhanced_communication.stream_progress("项目分析", 0.4, "分析代码质量")
    await enhanced_communication.stream_progress("项目分析", 0.6, "检查依赖关系")
    await enhanced_communication.stream_progress("项目分析", 0.8, "生成分析报告")
    await enhanced_communication.stream_progress("项目分析", 1.0, "分析完成")
    await enhanced_communication.stream_message("系统: 项目分析完成，发现3个改进建议", "system")
    
    print(f"聊天消息数: {len(web_ui.chat_messages)}")
    print(f"进度更新数: {len(web_ui.progress_updates)}")
    print(f"工具执行数: {len(web_ui.tool_executions)}")

if __name__ == "__main__":
    print("🚀 启动 Agent Zero 启发演示...")
    asyncio.run(demo_agent_zero_inspiration())
    asyncio.run(demo_web_ui_integration()) 