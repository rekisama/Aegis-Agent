"""
Smart Error Handling Core
智能错误处理核心系统，集成到主agent中
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

import sys
from pathlib import Path
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from python.tools.base import ToolResult
from python.agent.error_handler import ErrorHandlerAgent
from python.tools.enhanced_terminal import EnhancedTerminalTool, ErrorAnalyzer


@dataclass
class ErrorHandlingContext:
    """错误处理上下文"""
    original_command: str
    error_message: str
    error_type: str
    suggested_fix: str
    auto_fix_attempted: bool
    auto_fix_success: bool
    retry_count: int
    max_retries: int


class SmartErrorCore:
    """智能错误处理核心"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.error_handler = ErrorHandlerAgent(llm_client)
        self.terminal_tool = EnhancedTerminalTool()
        self.error_contexts = []
        self.auto_fix_enabled = True
        self.max_retries = 3
        self.verbose_logging = True
    
    async def execute_with_smart_error_handling(
        self, 
        command: str, 
        context: str = "",
        user_confirmation_required: bool = False
    ) -> Dict[str, Any]:
        """
        执行命令并智能处理错误
        
        Args:
            command: 要执行的命令
            context: 执行上下文
            user_confirmation_required: 是否需要用户确认
            
        Returns:
            执行结果字典
        """
        
        if self.verbose_logging:
            logging.info(f"🔧 智能错误处理: 执行命令 '{command}'")
        
        # 执行命令并处理错误
        result = await self.error_handler.execute_with_auto_fix(
            command=command,
            max_attempts=self.max_retries,
            context=context
        )
        
        # 创建错误处理上下文
        error_context = ErrorHandlingContext(
            original_command=command,
            error_message=result.get('final_error', ''),
            error_type=self._extract_error_type(result),
            suggested_fix=self._extract_suggested_fix(result),
            auto_fix_attempted=result.get('auto_fixes_applied', 0) > 0,
            auto_fix_success=result['success'],
            retry_count=result['attempts'],
            max_retries=self.max_retries
        )
        
        self.error_contexts.append(error_context)
        
        # 生成详细报告
        report = await self._generate_error_report(error_context, result)
        
        if self.verbose_logging:
            self._log_execution_summary(error_context, result)
        
        return {
            "success": result['success'],
            "command": command,
            "attempts": result['attempts'],
            "auto_fixes_applied": result['auto_fixes_applied'],
            "error_context": error_context,
            "report": report,
            "raw_result": result
        }
    
    def _extract_error_type(self, result: Dict[str, Any]) -> str:
        """提取错误类型"""
        if result['success']:
            return "success"
        
        # 从错误处理代理的结果中提取错误类型
        if 'raw_result' in result and 'error_analysis' in result['raw_result']:
            return result['raw_result']['error_analysis']['error_type'].value
        
        return "unknown"
    
    def _extract_suggested_fix(self, result: Dict[str, Any]) -> str:
        """提取修复建议"""
        if result['success']:
            return "无需修复"
        
        # 从错误处理代理的结果中提取修复建议
        if 'raw_result' in result and 'fix_suggestion' in result['raw_result']:
            return result['raw_result']['fix_suggestion']
        
        return "请检查命令和参数"
    
    async def _generate_error_report(
        self, 
        error_context: ErrorHandlingContext, 
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成错误报告"""
        
        report = {
            "execution_summary": {
                "command": error_context.original_command,
                "success": error_context.auto_fix_success,
                "attempts": error_context.retry_count,
                "auto_fixes_applied": result['auto_fixes_applied']
            },
            "error_analysis": {
                "error_type": error_context.error_type,
                "error_message": error_context.error_message,
                "suggested_fix": error_context.suggested_fix
            },
            "auto_fix_details": {
                "attempted": error_context.auto_fix_attempted,
                "successful": error_context.auto_fix_success,
                "fixes_applied": result['auto_fixes_applied']
            }
        }
        
        # 如果启用了LLM，生成更详细的建议
        if self.llm_client and not error_context.auto_fix_success:
            detailed_suggestion = await self._generate_llm_suggestion(error_context)
            report["llm_suggestion"] = detailed_suggestion
        
        return report
    
    async def _generate_llm_suggestion(self, error_context: ErrorHandlingContext) -> str:
        """使用LLM生成详细建议"""
        
        prompt = f"""
分析以下命令执行错误并提供详细的修复建议：

命令: {error_context.original_command}
错误类型: {error_context.error_type}
错误信息: {error_context.error_message}
已尝试的修复: {error_context.suggested_fix}

请提供：
1. 错误原因分析
2. 具体的修复步骤
3. 预防措施
4. 替代方案（如果有）
        """
        
        try:
            response = await self.llm_client.chat(prompt)
            return response
        except Exception as e:
            logging.warning(f"LLM建议生成失败: {e}")
            return "无法生成LLM建议"
    
    def _log_execution_summary(self, error_context: ErrorHandlingContext, result: Dict[str, Any]):
        """记录执行摘要"""
        
        if error_context.auto_fix_success:
            logging.info(f"✅ 命令执行成功: {error_context.original_command}")
            if error_context.auto_fix_attempted:
                logging.info(f"  自动修复次数: {result['auto_fixes_applied']}")
        else:
            logging.warning(f"❌ 命令执行失败: {error_context.original_command}")
            logging.warning(f"  错误类型: {error_context.error_type}")
            logging.warning(f"  错误信息: {error_context.error_message}")
            if error_context.auto_fix_attempted:
                logging.info(f"  已尝试自动修复: {result['auto_fixes_applied']} 次")
    
    async def handle_user_confirmation(
        self, 
        command: str, 
        suggested_fix: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """处理用户确认的修复操作"""
        
        logging.info(f"🔍 等待用户确认修复操作")
        logging.info(f"  原始命令: {command}")
        logging.info(f"  建议修复: {suggested_fix}")
        
        # 这里可以集成用户交互界面
        # 目前返回模拟的确认结果
        user_confirmed = True  # 模拟用户确认
        
        if user_confirmed:
            logging.info(f"✅ 用户确认执行修复操作")
            return await self.execute_with_smart_error_handling(
                command=suggested_fix,
                context=f"用户确认的修复操作: {context}",
                user_confirmation_required=False
            )
        else:
            logging.info(f"❌ 用户取消修复操作")
            return {
                "success": False,
                "reason": "用户取消修复操作",
                "command": command,
                "suggested_fix": suggested_fix
            }
    
    async def batch_execute_with_error_handling(
        self, 
        commands: List[str], 
        context: str = ""
    ) -> List[Dict[str, Any]]:
        """批量执行命令并处理错误"""
        
        results = []
        
        for i, command in enumerate(commands, 1):
            logging.info(f"🔄 执行命令 {i}/{len(commands)}: {command}")
            
            result = await self.execute_with_smart_error_handling(
                command=command,
                context=f"{context} (命令 {i}/{len(commands)})"
            )
            
            results.append(result)
            
            # 如果命令失败且不是最后一个，可以选择是否继续
            if not result['success'] and i < len(commands):
                logging.warning(f"命令 {i} 失败，继续执行下一个命令")
        
        return results
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        
        total_executions = len(self.error_contexts)
        successful_executions = len([ctx for ctx in self.error_contexts if ctx.auto_fix_success])
        failed_executions = total_executions - successful_executions
        
        error_types = {}
        for ctx in self.error_contexts:
            error_type = ctx.error_type
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        auto_fix_stats = {
            "total_attempts": len([ctx for ctx in self.error_contexts if ctx.auto_fix_attempted]),
            "successful_fixes": len([ctx for ctx in self.error_contexts if ctx.auto_fix_attempted and ctx.auto_fix_success])
        }
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "error_types": error_types,
            "auto_fix_stats": auto_fix_stats
        }
    
    def clear_history(self):
        """清除历史记录"""
        self.error_contexts.clear()
        self.error_handler.clear_history()
        logging.info("智能错误处理历史已清除")
    
    def set_auto_fix_enabled(self, enabled: bool):
        """设置是否启用自动修复"""
        self.auto_fix_enabled = enabled
        logging.info(f"自动修复已{'启用' if enabled else '禁用'}")
    
    def set_max_retries(self, max_retries: int):
        """设置最大重试次数"""
        self.max_retries = max_retries
        logging.info(f"最大重试次数设置为: {max_retries}")
    
    def set_verbose_logging(self, verbose: bool):
        """设置详细日志"""
        self.verbose_logging = verbose
        logging.info(f"详细日志已{'启用' if verbose else '禁用'}")


class SmartErrorIntegration:
    """智能错误处理集成器"""
    
    def __init__(self, agent_core):
        self.agent_core = agent_core
        self.smart_error_core = SmartErrorCore()
        self.integration_enabled = True
    
    async def integrate_with_agent_execution(
        self, 
        task: str, 
        tools_to_use: List[str] = None
    ) -> Dict[str, Any]:
        """集成到agent执行流程中"""
        
        if not self.integration_enabled:
            return await self.agent_core.execute_task(task, tools_to_use)
        
        logging.info(f"🤖 智能错误处理集成: 执行任务 '{task}'")
        
        # 执行原始任务
        original_result = await self.agent_core.execute_task(task, tools_to_use)
        
        # 检查是否有终端命令执行
        if self._contains_terminal_commands(original_result):
            logging.info("🔍 检测到终端命令，启用智能错误处理")
            
            # 提取终端命令并重新执行
            terminal_commands = self._extract_terminal_commands(original_result)
            
            for command in terminal_commands:
                smart_result = await self.smart_error_core.execute_with_smart_error_handling(
                    command=command,
                    context=f"Agent任务: {task}"
                )
                
                # 如果智能处理成功，更新结果
                if smart_result['success'] and not original_result.get('success', True):
                    original_result['success'] = True
                    original_result['smart_error_handling'] = smart_result
                    logging.info(f"✅ 智能错误处理成功修复了命令: {command}")
        
        return original_result
    
    def _contains_terminal_commands(self, result: Dict[str, Any]) -> bool:
        """检查结果是否包含终端命令"""
        # 这里可以根据实际的结果结构来判断
        return "terminal" in str(result).lower() or "command" in str(result).lower()
    
    def _extract_terminal_commands(self, result: Dict[str, Any]) -> List[str]:
        """提取终端命令"""
        # 这里需要根据实际的结果结构来提取命令
        # 这是一个简化的实现
        commands = []
        
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, str) and any(cmd in value.lower() for cmd in ['python', 'pip', 'apt', 'sudo']):
                    commands.append(value)
                elif isinstance(value, dict):
                    commands.extend(self._extract_terminal_commands(value))
        
        return commands
    
    def enable_integration(self):
        """启用集成"""
        self.integration_enabled = True
        logging.info("智能错误处理集成已启用")
    
    def disable_integration(self):
        """禁用集成"""
        self.integration_enabled = False
        logging.info("智能错误处理集成已禁用")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        return {
            "enabled": self.integration_enabled,
            "smart_error_core_stats": self.smart_error_core.get_error_statistics()
        } 