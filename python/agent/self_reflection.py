"""
Self-Reflection System for Self-Evolving Agent
自我反思系统，允许 Agent 分析自己的表现并提出改进建议
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..llm.deepseek_client import DeepSeekClient


@dataclass
class ReflectionSession:
    """反思会话"""
    session_id: str
    task_id: str
    task_description: str
    execution_summary: Dict[str, Any]
    self_analysis: Dict[str, Any]
    improvement_suggestions: List[str]
    created_at: str


class SelfReflectionSystem:
    """
    自我反思系统
    分析 Agent 的表现，识别改进机会
    """
    
    def __init__(self):
        self.reflection_sessions: List[ReflectionSession] = []
    
    async def analyze_performance(self, task_id: str, task_description: str, 
                                execution_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析任务执行表现
        
        Args:
            task_id: 任务ID
            task_description: 任务描述
            execution_summary: 执行摘要
            
        Returns:
            Dict: 反思结果
        """
        try:
            # 使用 LLM 进行自我分析
            analysis_result = await self._perform_self_analysis(
                task_description, execution_summary
            )
            
            # 生成改进建议
            improvement_suggestions = await self._generate_improvement_suggestions(
                analysis_result, execution_summary
            )
            
            # 创建反思会话
            reflection_session = ReflectionSession(
                session_id=f"reflection_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                task_id=task_id,
                task_description=task_description,
                execution_summary=execution_summary,
                self_analysis=analysis_result,
                improvement_suggestions=improvement_suggestions,
                created_at=datetime.now().isoformat()
            )
            
            self.reflection_sessions.append(reflection_session)
            
            return {
                "session_id": reflection_session.session_id,
                "analysis": analysis_result,
                "suggestions": improvement_suggestions,
                "overall_score": self._calculate_overall_score(analysis_result)
            }
            
        except Exception as e:
            logging.error(f"Failed to analyze performance: {e}")
            return {
                "error": str(e),
                "analysis": {},
                "suggestions": ["无法完成自我分析"],
                "overall_score": 0.0
            }
    
    async def _perform_self_analysis(self, task_description: str, 
                                   execution_summary: Dict[str, Any]) -> Dict[str, Any]:
        """执行自我分析"""
        try:
            async with DeepSeekClient() as llm_client:
                system_prompt = """You are an AI agent performing self-reflection on your task execution.

Analyze your performance objectively and provide insights on:
1. Task understanding accuracy
2. Tool selection effectiveness
3. Execution efficiency
4. Result quality
5. Areas for improvement

Be honest and constructive in your analysis."""

                prompt = f"""Task: {task_description}

Execution Summary:
{json.dumps(execution_summary, indent=2, ensure_ascii=False)}

Please analyze your performance and provide:
1. What went well
2. What could be improved
3. Specific areas for enhancement
4. Learning opportunities

Respond in JSON format:
{{
    "task_understanding_score": 0.0-1.0,
    "tool_selection_score": 0.0-1.0,
    "execution_efficiency_score": 0.0-1.0,
    "result_quality_score": 0.0-1.0,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "key_learnings": ["learning1", "learning2"],
    "analysis_summary": "detailed analysis text"
}}"""

                result = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=800
                )
                
                if result["success"]:
                    try:
                        analysis = json.loads(result["content"])
                        return analysis
                    except json.JSONDecodeError:
                        return self._fallback_analysis(execution_summary)
                else:
                    return self._fallback_analysis(execution_summary)
                    
        except Exception as e:
            logging.error(f"Self-analysis failed: {e}")
            return self._fallback_analysis(execution_summary)
    
    def _fallback_analysis(self, execution_summary: Dict[str, Any]) -> Dict[str, Any]:
        """回退分析"""
        success_rate = execution_summary.get("success_rate", 0.0)
        execution_time = execution_summary.get("execution_time", 0.0)
        
        return {
            "task_understanding_score": 0.7 if success_rate > 0.5 else 0.3,
            "tool_selection_score": 0.6,
            "execution_efficiency_score": 0.8 if execution_time < 30 else 0.4,
            "result_quality_score": success_rate,
            "strengths": ["Basic task execution capability"],
            "weaknesses": ["Limited self-analysis capability"],
            "key_learnings": ["Need to improve self-reflection"],
            "analysis_summary": "Basic performance analysis completed"
        }
    
    async def _generate_improvement_suggestions(self, analysis: Dict[str, Any], 
                                             execution_summary: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        try:
            async with DeepSeekClient() as llm_client:
                system_prompt = """You are an AI coach helping an AI agent improve its performance.

Based on the performance analysis, provide specific, actionable improvement suggestions.
Focus on practical steps the agent can take to enhance its capabilities."""

                prompt = f"""Performance Analysis:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

Execution Summary:
{json.dumps(execution_summary, indent=2, ensure_ascii=False)}

Please provide 3-5 specific, actionable improvement suggestions.
Focus on:
1. Tool selection and usage
2. Task understanding and planning
3. Execution efficiency
4. Result quality improvement

Respond with a JSON array of suggestions:
["suggestion1", "suggestion2", "suggestion3"]"""

                result = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.5,
                    max_tokens=500
                )
                
                if result["success"]:
                    try:
                        suggestions = json.loads(result["content"])
                        if isinstance(suggestions, list):
                            return suggestions
                    except json.JSONDecodeError:
                        pass
                
                # 回退建议
                return self._generate_fallback_suggestions(analysis)
                
        except Exception as e:
            logging.error(f"Failed to generate improvement suggestions: {e}")
            return self._generate_fallback_suggestions(analysis)
    
    def _generate_fallback_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成回退建议"""
        suggestions = []
        
        if analysis.get("tool_selection_score", 0.0) < 0.7:
            suggestions.append("改进工具选择策略，分析任务需求并选择最合适的工具")
        
        if analysis.get("execution_efficiency_score", 0.0) < 0.7:
            suggestions.append("优化执行流程，减少不必要的步骤和等待时间")
        
        if analysis.get("result_quality_score", 0.0) < 0.7:
            suggestions.append("提高结果质量，增加验证和测试步骤")
        
        if not suggestions:
            suggestions.append("继续收集更多执行数据以改进分析")
        
        return suggestions
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """计算总体评分"""
        scores = [
            analysis.get("task_understanding_score", 0.0),
            analysis.get("tool_selection_score", 0.0),
            analysis.get("execution_efficiency_score", 0.0),
            analysis.get("result_quality_score", 0.0)
        ]
        
        return sum(scores) / len(scores) if scores else 0.0
    
    async def generate_learning_report(self, days: int = 7) -> Dict[str, Any]:
        """生成学习报告"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_sessions = [
                session for session in self.reflection_sessions
                if datetime.fromisoformat(session.created_at) > cutoff_date
            ]
            
            if not recent_sessions:
                return {
                    "period": f"Last {days} days",
                    "total_sessions": 0,
                    "average_score": 0.0,
                    "improvement_areas": [],
                    "strengths": [],
                    "recommendations": ["需要更多执行数据来生成学习报告"]
                }
            
            # 计算统计数据
            total_sessions = len(recent_sessions)
            average_score = sum(
                self._calculate_overall_score(session.self_analysis)
                for session in recent_sessions
            ) / total_sessions
            
            # 分析改进领域
            all_weaknesses = []
            all_strengths = []
            
            for session in recent_sessions:
                analysis = session.self_analysis
                all_weaknesses.extend(analysis.get("weaknesses", []))
                all_strengths.extend(analysis.get("strengths", []))
            
            # 统计最常见的改进领域
            weakness_counts = {}
            for weakness in all_weaknesses:
                weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
            
            improvement_areas = sorted(
                weakness_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            # 统计优势
            strength_counts = {}
            for strength in all_strengths:
                strength_counts[strength] = strength_counts.get(strength, 0) + 1
            
            top_strengths = sorted(
                strength_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            return {
                "period": f"Last {days} days",
                "total_sessions": total_sessions,
                "average_score": round(average_score, 3),
                "improvement_areas": [area[0] for area in improvement_areas],
                "strengths": [strength[0] for strength in top_strengths],
                "recommendations": self._generate_period_recommendations(
                    average_score, improvement_areas
                )
            }
            
        except Exception as e:
            logging.error(f"Failed to generate learning report: {e}")
            return {
                "error": str(e),
                "period": f"Last {days} days",
                "total_sessions": 0,
                "average_score": 0.0,
                "improvement_areas": [],
                "strengths": [],
                "recommendations": ["无法生成学习报告"]
            }
    
    def _generate_period_recommendations(self, average_score: float, 
                                       improvement_areas: List[tuple]) -> List[str]:
        """生成期间建议"""
        recommendations = []
        
        if average_score < 0.6:
            recommendations.append("整体表现需要显著改进，建议增加更多练习和测试")
        elif average_score < 0.8:
            recommendations.append("表现良好，但仍有改进空间")
        else:
            recommendations.append("表现优秀，继续保持")
        
        if improvement_areas:
            top_area = improvement_areas[0][0]
            recommendations.append(f"重点关注改进：{top_area}")
        
        return recommendations
    
    def get_reflection_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取反思历史"""
        recent_sessions = sorted(
            self.reflection_sessions,
            key=lambda x: x.created_at,
            reverse=True
        )[:limit]
        
        return [
            {
                "session_id": session.session_id,
                "task_id": session.task_id,
                "task_description": session.task_description,
                "overall_score": self._calculate_overall_score(session.self_analysis),
                "created_at": session.created_at,
                "improvement_suggestions": session.improvement_suggestions[:3]  # 只显示前3个建议
            }
            for session in recent_sessions
        ]
    
    def export_reflection_data(self, filepath: str):
        """导出反思数据"""
        try:
            data = {
                "reflection_sessions": [
                    asdict(session) for session in self.reflection_sessions
                ],
                "export_date": datetime.now().isoformat(),
                "total_sessions": len(self.reflection_sessions)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Exported reflection data to {filepath}")
            
        except Exception as e:
            logging.error(f"Failed to export reflection data: {e}")


# 全局自我反思系统实例
self_reflection = SelfReflectionSystem() 