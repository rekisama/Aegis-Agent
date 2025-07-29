#!/usr/bin/env python3
"""
Tool Management CLI
提供命令行工具来管理JSON工具注册表
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from python.tools.json_tool_manager import JSONToolManager, ToolInfo, ToolStatus


def list_tools(manager: JSONToolManager, show_details: bool = False):
    """列出所有工具"""
    print("🔧 Available Tools:")
    print("=" * 50)
    
    for tool_name, tool_info in manager.tools.items():
        status_icon = {
            ToolStatus.DISCOVERED: "🔍",
            ToolStatus.LOADED: "✅",
            ToolStatus.ACTIVE: "🟢",
            ToolStatus.ERROR: "❌",
            ToolStatus.DISABLED: "🚫",
            ToolStatus.UNLOADED: "⏸️"
        }.get(tool_info.status, "❓")
        
        print(f"{status_icon} {tool_name}")
        print(f"   Description: {tool_info.description}")
        print(f"   Category: {tool_info.category}")
        print(f"   Status: {tool_info.status.value}")
        print(f"   Enabled: {tool_info.enabled}")
        print(f"   Auto Load: {tool_info.auto_load}")
        
        if tool_info.aliases:
            print(f"   Aliases: {', '.join(tool_info.aliases)}")
        
        if show_details:
            print(f"   Class: {tool_info.class_name}")
            print(f"   Module: {tool_info.module_path}")
            print(f"   Version: {tool_info.version}")
            print(f"   Author: {tool_info.author}")
            
            if tool_info.dependencies:
                print(f"   Dependencies: {', '.join(tool_info.dependencies)}")
            
            if tool_info.config_schema:
                print(f"   Config Schema: {json.dumps(tool_info.config_schema, indent=2)}")
        
        print()


def add_tool(manager: JSONToolManager, tool_data: Dict[str, Any]):
    """添加新工具"""
    try:
        tool_info = ToolInfo(
            name=tool_data["name"],
            description=tool_data["description"],
            class_name=tool_data["class"],
            module_path=tool_data["module"],
            aliases=tool_data.get("aliases", []),
            category=tool_data.get("category", "general"),
            enabled=tool_data.get("enabled", True),
            auto_load=tool_data.get("auto_load", True),
            version=tool_data.get("version", "1.0.0"),
            author=tool_data.get("author", "Unknown"),
            dependencies=tool_data.get("dependencies", []),
            config_schema=tool_data.get("config_schema", {}),
            metadata=tool_data.get("metadata", {})
        )
        
        if manager.add_tool(tool_info):
            print(f"✅ Added tool: {tool_info.name}")
            manager._save_registry()
        else:
            print(f"❌ Failed to add tool: {tool_info.name}")
            
    except Exception as e:
        print(f"❌ Error adding tool: {e}")


def remove_tool(manager: JSONToolManager, tool_name: str):
    """移除工具"""
    if manager.remove_tool(tool_name):
        print(f"✅ Removed tool: {tool_name}")
        manager._save_registry()
    else:
        print(f"❌ Failed to remove tool: {tool_name}")


def enable_tool(manager: JSONToolManager, tool_name: str):
    """启用工具"""
    if manager.enable_tool(tool_name):
        print(f"✅ Enabled tool: {tool_name}")
        manager._save_registry()
    else:
        print(f"❌ Failed to enable tool: {tool_name}")


def disable_tool(manager: JSONToolManager, tool_name: str):
    """禁用工具"""
    if manager.disable_tool(tool_name):
        print(f"✅ Disabled tool: {tool_name}")
        manager._save_registry()
    else:
        print(f"❌ Failed to disable tool: {tool_name}")


def reload_tool(manager: JSONToolManager, tool_name: str):
    """重新加载工具"""
    tool = manager.reload_tool(tool_name)
    if tool:
        print(f"✅ Reloaded tool: {tool_name}")
    else:
        print(f"❌ Failed to reload tool: {tool_name}")


def test_tool(manager: JSONToolManager, tool_name: str):
    """测试工具"""
    tool = manager.get_tool(tool_name)
    if tool:
        print(f"✅ Tool '{tool_name}' is available")
        print(f"   Type: {type(tool).__name__}")
        print(f"   Description: {tool.description}")
    else:
        print(f"❌ Tool '{tool_name}' is not available")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Tool Management CLI")
    parser.add_argument("command", choices=["list", "add", "remove", "enable", "disable", "reload", "test"])
    parser.add_argument("--tool", help="Tool name")
    parser.add_argument("--details", action="store_true", help="Show detailed information")
    parser.add_argument("--config", help="Tool configuration file (JSON)")
    
    args = parser.parse_args()
    
    # 创建工具管理器
    manager = JSONToolManager()
    
    if args.command == "list":
        list_tools(manager, args.details)
    
    elif args.command == "add":
        if not args.config:
            print("❌ Please provide a configuration file with --config")
            return
        
        try:
            with open(args.config, 'r') as f:
                tool_data = json.load(f)
            add_tool(manager, tool_data)
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
    
    elif args.command == "remove":
        if not args.tool:
            print("❌ Please provide a tool name with --tool")
            return
        remove_tool(manager, args.tool)
    
    elif args.command == "enable":
        if not args.tool:
            print("❌ Please provide a tool name with --tool")
            return
        enable_tool(manager, args.tool)
    
    elif args.command == "disable":
        if not args.tool:
            print("❌ Please provide a tool name with --tool")
            return
        disable_tool(manager, args.tool)
    
    elif args.command == "reload":
        if not args.tool:
            print("❌ Please provide a tool name with --tool")
            return
        reload_tool(manager, args.tool)
    
    elif args.command == "test":
        if not args.tool:
            print("❌ Please provide a tool name with --tool")
            return
        test_tool(manager, args.tool)


if __name__ == "__main__":
    main() 