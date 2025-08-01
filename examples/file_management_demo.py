#!/usr/bin/env python3
"""
Agent文件管理演示
演示新的工作区文件管理功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from python.tools.file_manager import FileManagerTool
from python.tools.base import ToolResult

async def demo_workspace_structure():
    """演示工作区结构"""
    print("=== Agent文件管理工作区演示 ===\n")
    
    # 初始化文件管理工具
    file_manager = FileManagerTool()
    
    # 获取工作区信息
    result = await file_manager.execute(action="get_workspace_info")
    if result.success:
        info = result.data
        print(f"工作区目录: {info['workspace_dir']}")
        print(f"输入目录: {info['input_dir']}")
        print(f"输出目录: {info['output_dir']}")
        print(f"临时目录: {info['temp_dir']}")
        print(f"描述: {info['description']}")
        print()
    
    # 列出工作区内容
    result = await file_manager.execute(action="list", directory="workspace")
    if result.success:
        data = result.data
        print(f"工作区内容 (目录: {data['total_dirs']}, 文件: {data['total_files']}):")
        for dir_info in data['directories']:
            print(f"  📁 {dir_info['name']}")
        for file_info in data['files']:
            print(f"  📄 {file_info['name']} ({file_info['size']} bytes)")
        print()

async def demo_file_operations():
    """演示文件操作"""
    print("=== 文件操作演示 ===\n")
    
    file_manager = FileManagerTool()
    
    # 1. 上传文件到输入目录
    print("1. 上传文件到输入目录...")
    result = await file_manager.execute(
        action="upload",
        file_name="input_data.txt",
        content="这是输入数据文件\n包含一些测试数据",
        target_dir="input"
    )
    if result.success:
        print(f"   ✅ 上传成功: {result.data['message']}")
    else:
        print(f"   ❌ 上传失败: {result.error}")
    
    # 2. 上传文件到输出目录
    print("\n2. 上传文件到输出目录...")
    result = await file_manager.execute(
        action="upload",
        file_name="output_result.txt",
        content="这是输出结果文件\n包含处理结果",
        target_dir="output"
    )
    if result.success:
        print(f"   ✅ 上传成功: {result.data['message']}")
    else:
        print(f"   ❌ 上传失败: {result.error}")
    
    # 3. 创建临时文件
    print("\n3. 创建临时文件...")
    result = await file_manager.execute(
        action="upload",
        file_name="temp_work.txt",
        content="这是临时工作文件",
        target_dir="temp"
    )
    if result.success:
        print(f"   ✅ 创建成功: {result.data['message']}")
    else:
        print(f"   ❌ 创建失败: {result.error}")
    
    # 4. 列出各目录内容
    print("\n4. 列出各目录内容...")
    for dir_name in ["input", "output", "temp"]:
        result = await file_manager.execute(action="list", directory=dir_name)
        if result.success:
            data = result.data
            print(f"   📁 {dir_name}目录:")
            for file_info in data['files']:
                print(f"     📄 {file_info['name']} ({file_info['size']} bytes)")
        else:
            print(f"   ❌ 列出{dir_name}目录失败: {result.error}")
    
    # 5. 移动文件
    print("\n5. 移动文件...")
    result = await file_manager.execute(
        action="move",
        source_path="input/input_data.txt",
        target_path="output/processed_input.txt"
    )
    if result.success:
        print(f"   ✅ 移动成功: {result.data['message']}")
    else:
        print(f"   ❌ 移动失败: {result.error}")
    
    # 6. 复制文件
    print("\n6. 复制文件...")
    result = await file_manager.execute(
        action="copy",
        source_path="output/output_result.txt",
        target_path="temp/backup_result.txt"
    )
    if result.success:
        print(f"   ✅ 复制成功: {result.data['message']}")
    else:
        print(f"   ❌ 复制失败: {result.error}")
    
    # 7. 获取文件信息
    print("\n7. 获取文件信息...")
    result = await file_manager.execute(
        action="get_info",
        file_path="output/output_result.txt"
    )
    if result.success:
        info = result.data
        print(f"   📄 文件信息:")
        print(f"     名称: {info['file_name']}")
        print(f"     大小: {info['size_formatted']}")
        print(f"     修改时间: {info['modified_formatted']}")
    else:
        print(f"   ❌ 获取文件信息失败: {result.error}")
    
    # 8. 下载文件
    print("\n8. 下载文件...")
    result = await file_manager.execute(
        action="download",
        file_path="output/output_result.txt"
    )
    if result.success:
        import base64
        content = base64.b64decode(result.data['content']).decode('utf-8')
        print(f"   ✅ 下载成功: {result.data['file_name']}")
        print(f"   内容: {content}")
    else:
        print(f"   ❌ 下载失败: {result.error}")

async def demo_agent_workflow():
    """演示Agent工作流程"""
    print("\n=== Agent工作流程演示 ===\n")
    
    file_manager = FileManagerTool()
    
    # 模拟Agent处理流程
    print("🤖 Agent开始处理任务...")
    
    # 1. 检查输入文件
    print("\n1. 检查输入文件...")
    result = await file_manager.execute(action="list", directory="input")
    if result.success:
        input_files = result.data['files']
        if input_files:
            print(f"   发现 {len(input_files)} 个输入文件:")
            for file_info in input_files:
                print(f"     📄 {file_info['name']}")
        else:
            print("   没有发现输入文件")
    
    # 2. 处理文件（模拟）
    print("\n2. 处理文件...")
    # 这里可以添加实际的文件处理逻辑
    
    # 3. 生成输出文件
    print("\n3. 生成输出文件...")
    result = await file_manager.execute(
        action="upload",
        file_name="analysis_report.txt",
        content="分析报告\n\n处理时间: 2024-01-01\n处理结果: 成功\n\n详细内容...",
        target_dir="output"
    )
    if result.success:
        print(f"   ✅ 生成报告成功: {result.data['message']}")
    else:
        print(f"   ❌ 生成报告失败: {result.error}")
    
    # 4. 清理临时文件
    print("\n4. 清理临时文件...")
    result = await file_manager.execute(action="list", directory="temp")
    if result.success:
        temp_files = result.data['files']
        for file_info in temp_files:
            delete_result = await file_manager.execute(
                action="delete",
                file_path=f"temp/{file_info['name']}"
            )
            if delete_result.success:
                print(f"   🗑️ 删除临时文件: {file_info['name']}")
            else:
                print(f"   ❌ 删除失败: {delete_result.error}")
    
    # 5. 最终状态
    print("\n5. 最终状态...")
    for dir_name in ["input", "output", "temp"]:
        result = await file_manager.execute(action="list", directory=dir_name)
        if result.success:
            data = result.data
            print(f"   📁 {dir_name}目录: {data['total_files']} 个文件")
        else:
            print(f"   ❌ 检查{dir_name}目录失败: {result.error}")

async def main():
    """主函数"""
    try:
        await demo_workspace_structure()
        await demo_file_operations()
        await demo_agent_workflow()
        
        print("\n=== 演示完成 ===")
        print("新的文件管理系统特点:")
        print("✅ 专门的工作区结构 (input/output/temp)")
        print("✅ 安全的文件隔离")
        print("✅ 清晰的文件组织")
        print("✅ 支持完整的文件操作")
        print("✅ 适合Agent自动化处理")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 