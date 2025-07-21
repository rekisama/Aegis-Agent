"""
Adaptive Learning System for Self-Evolving Agent
自适应学习系统，允许 Agent 从经验中学习和改进
"""

import json
import logging
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from .tool_descriptions import ToolCategory


@dataclass
class LearningExperience:
    """学习经验记录"""
    task_id: str
    task_description: str
    task_type: str
    tools_used: List[str]
    success: bool
    execution_time: float
    result_quality: float  # 0-1 质量评分
    user_feedback: Optional[str] = None
    learned_patterns: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.learned_patterns is None:
            self.learned_patterns = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ToolPerformance:
    """工具性能记录"""
    tool_name: str
    usage_count: int
    success_count: int
    avg_execution_time: float
    last_used: str
    success_rate: float = 0.0
    
    def update_success_rate(self):
        """更新成功率"""
        if self.usage_count > 0:
            self.success_rate = self.success_count / self.usage_count


class AdaptiveLearningSystem:
    """
    自适应学习系统
    记录和分析 Agent 的执行经验，提供学习建议
    """
    
    def __init__(self, db_path: str = "memory/learning.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE,
                    task_description TEXT,
                    task_type TEXT,
                    tools_used TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    result_quality REAL,
                    user_feedback TEXT,
                    learned_patterns TEXT,
                    created_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_performance (
                    tool_name TEXT PRIMARY KEY,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    avg_execution_time REAL DEFAULT 0,
                    last_used TEXT,
                    success_rate REAL DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_description TEXT,
                    task_type TEXT,
                    recommended_tools TEXT,
                    success_rate REAL,
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)
            
            conn.commit()
    
    def record_experience(self, experience: LearningExperience):
        """记录学习经验"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO learning_experiences 
                    (task_id, task_description, task_type, tools_used, success, 
                     execution_time, result_quality, user_feedback, learned_patterns, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    experience.task_id,
                    experience.task_description,
                    experience.task_type,
                    json.dumps(experience.tools_used),
                    experience.success,
                    experience.execution_time,
                    experience.result_quality,
                    experience.user_feedback,
                    json.dumps(experience.learned_patterns),
                    experience.created_at
                ))
                conn.commit()
                
            # 更新工具性能统计
            self._update_tool_performance(experience)
            
            # 分析并记录任务模式
            self._analyze_task_pattern(experience)
            
            logging.info(f"Recorded learning experience for task: {experience.task_id}")
            
        except Exception as e:
            logging.error(f"Failed to record learning experience: {e}")
    
    def _update_tool_performance(self, experience: LearningExperience):
        """更新工具性能统计"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for tool_name in experience.tools_used:
                    # 获取现有记录
                    cursor = conn.execute(
                        "SELECT * FROM tool_performance WHERE tool_name = ?",
                        (tool_name,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        # 更新现有记录
                        usage_count = row[1] + 1
                        success_count = row[2] + (1 if experience.success else 0)
                        avg_time = (row[3] * row[1] + experience.execution_time) / usage_count
                        
                        conn.execute("""
                            UPDATE tool_performance 
                            SET usage_count = ?, success_count = ?, avg_execution_time = ?, 
                                last_used = ?, success_rate = ?
                            WHERE tool_name = ?
                        """, (
                            usage_count, success_count, avg_time,
                            experience.created_at,
                            success_count / usage_count,
                            tool_name
                        ))
                    else:
                        # 创建新记录
                        conn.execute("""
                            INSERT INTO tool_performance 
                            (tool_name, usage_count, success_count, avg_execution_time, last_used, success_rate)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            tool_name, 1, 1 if experience.success else 0,
                            experience.execution_time, experience.created_at,
                            1.0 if experience.success else 0.0
                        ))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Failed to update tool performance: {e}")
    
    def _analyze_task_pattern(self, experience: LearningExperience):
        """分析任务模式"""
        try:
            # 简单的模式识别：基于任务类型和工具组合
            pattern_id = self._generate_pattern_id(experience)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM task_patterns WHERE pattern_id = ?",
                    (pattern_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    # 更新现有模式
                    usage_count = row[5] + 1
                    success_count = int(row[4] * row[5]) + (1 if experience.success else 0)
                    new_success_rate = success_count / usage_count
                    
                    conn.execute("""
                        UPDATE task_patterns 
                        SET usage_count = ?, success_rate = ?
                        WHERE pattern_id = ?
                    """, (usage_count, new_success_rate, pattern_id))
                else:
                    # 创建新模式
                    conn.execute("""
                        INSERT INTO task_patterns 
                        (pattern_id, pattern_description, task_type, recommended_tools, 
                         success_rate, usage_count, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pattern_id,
                        f"Pattern for {experience.task_type} tasks",
                        experience.task_type,
                        json.dumps(experience.tools_used),
                        1.0 if experience.success else 0.0,
                        1,
                        experience.created_at
                    ))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Failed to analyze task pattern: {e}")
    
    def _generate_pattern_id(self, experience: LearningExperience) -> str:
        """生成模式ID"""
        pattern_data = f"{experience.task_type}:{','.join(sorted(experience.tools_used))}"
        return hashlib.md5(pattern_data.encode()).hexdigest()[:8]
    
    def get_recommendations(self, task_description: str, task_type: str = None) -> Dict[str, Any]:
        """获取任务执行建议"""
        try:
            recommendations = {
                "recommended_tools": [],
                "avoid_tools": [],
                "estimated_duration": "unknown",
                "success_probability": 0.5,
                "similar_experiences": []
            }
            
            with sqlite3.connect(self.db_path) as conn:
                # 查找相似任务模式
                if task_type:
                    cursor = conn.execute("""
                        SELECT * FROM task_patterns 
                        WHERE task_type = ? 
                        ORDER BY success_rate DESC, usage_count DESC
                        LIMIT 5
                    """, (task_type,))
                    
                    patterns = cursor.fetchall()
                    if patterns:
                        best_pattern = patterns[0]
                        recommendations["recommended_tools"] = json.loads(best_pattern[3])
                        recommendations["success_probability"] = best_pattern[4]
                
                # 获取工具性能建议
                cursor = conn.execute("""
                    SELECT tool_name, success_rate, usage_count 
                    FROM tool_performance 
                    WHERE usage_count >= 3
                    ORDER BY success_rate DESC
                """)
                
                tool_performance = cursor.fetchall()
                high_performance_tools = [row[0] for row in tool_performance if row[1] > 0.7]
                low_performance_tools = [row[0] for row in tool_performance if row[1] < 0.3]
                
                recommendations["recommended_tools"].extend(high_performance_tools)
                recommendations["avoid_tools"] = low_performance_tools
                
                # 查找相似经验
                cursor = conn.execute("""
                    SELECT task_description, tools_used, success, result_quality
                    FROM learning_experiences 
                    WHERE task_type = ? OR task_description LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 3
                """, (task_type or "", f"%{task_description[:20]}%"))
                
                similar_experiences = cursor.fetchall()
                recommendations["similar_experiences"] = [
                    {
                        "description": row[0],
                        "tools": json.loads(row[1]),
                        "success": row[2],
                        "quality": row[3]
                    }
                    for row in similar_experiences
                ]
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Failed to get recommendations: {e}")
            return recommendations
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """获取学习洞察"""
        try:
            insights = {
                "total_experiences": 0,
                "success_rate": 0.0,
                "most_used_tools": [],
                "best_performing_tools": [],
                "recent_patterns": [],
                "improvement_suggestions": []
            }
            
            with sqlite3.connect(self.db_path) as conn:
                # 总体统计
                cursor = conn.execute("""
                    SELECT COUNT(*), AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
                    FROM learning_experiences
                """)
                total, success_rate = cursor.fetchone()
                insights["total_experiences"] = total
                insights["success_rate"] = success_rate or 0.0
                
                # 最常用工具
                cursor = conn.execute("""
                    SELECT tool_name, usage_count 
                    FROM tool_performance 
                    ORDER BY usage_count DESC 
                    LIMIT 5
                """)
                insights["most_used_tools"] = [
                    {"tool": row[0], "usage": row[1]} 
                    for row in cursor.fetchall()
                ]
                
                # 最佳性能工具
                cursor = conn.execute("""
                    SELECT tool_name, success_rate 
                    FROM tool_performance 
                    WHERE usage_count >= 3
                    ORDER BY success_rate DESC 
                    LIMIT 5
                """)
                insights["best_performing_tools"] = [
                    {"tool": row[0], "success_rate": row[1]} 
                    for row in cursor.fetchall()
                ]
                
                # 最近模式
                cursor = conn.execute("""
                    SELECT pattern_description, success_rate, usage_count
                    FROM task_patterns 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                insights["recent_patterns"] = [
                    {"description": row[0], "success_rate": row[1], "usage": row[2]} 
                    for row in cursor.fetchall()
                ]
            
            # 生成改进建议
            insights["improvement_suggestions"] = self._generate_improvement_suggestions(insights)
            
            return insights
            
        except Exception as e:
            logging.error(f"Failed to get learning insights: {e}")
            return insights
    
    def _generate_improvement_suggestions(self, insights: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if insights["success_rate"] < 0.7:
            suggestions.append("成功率较低，建议分析失败案例并改进工具选择策略")
        
        if not insights["best_performing_tools"]:
            suggestions.append("工具使用数据不足，建议增加更多任务执行来收集数据")
        
        low_success_tools = [
            tool["tool"] for tool in insights["most_used_tools"]
            if tool["usage"] > 5 and tool["tool"] not in [t["tool"] for t in insights["best_performing_tools"]]
        ]
        
        if low_success_tools:
            suggestions.append(f"工具 {', '.join(low_success_tools)} 性能较差，建议优化或寻找替代方案")
        
        return suggestions
    
    def get_tool_performance_report(self) -> Dict[str, Any]:
        """获取工具性能报告"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT tool_name, usage_count, success_count, avg_execution_time, 
                           success_rate, last_used
                    FROM tool_performance 
                    ORDER BY usage_count DESC
                """)
                
                tools = []
                for row in cursor.fetchall():
                    tools.append({
                        "tool_name": row[0],
                        "usage_count": row[1],
                        "success_count": row[2],
                        "avg_execution_time": row[3],
                        "success_rate": row[4],
                        "last_used": row[5]
                    })
                
                return {
                    "total_tools": len(tools),
                    "tools": tools
                }
                
        except Exception as e:
            logging.error(f"Failed to get tool performance report: {e}")
            return {"total_tools": 0, "tools": []}
    
    def cleanup_old_data(self, days: int = 30):
        """清理旧数据"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM learning_experiences 
                    WHERE created_at < ?
                """, (cutoff_date,))
                
                conn.commit()
                
            logging.info(f"Cleaned up learning data older than {days} days")
            
        except Exception as e:
            logging.error(f"Failed to cleanup old data: {e}")

    def find_best_tools_for_task(self, task_description: str) -> List[str]:
        """使用 LLM 为任务找到最佳工具"""
        try:
            # 获取所有可用工具
            all_tools = list(self.tools.keys())
            if not all_tools:
                return []
            
            # 使用 LLM 分析任务并推荐工具
            return self._llm_tool_recommendation(task_description, all_tools)
            
        except Exception as e:
            logging.error(f"Failed to find best tools: {e}")
            return []
    
    def _llm_tool_recommendation(self, task_description: str, available_tools: List[str]) -> List[str]:
        """使用 LLM 推荐工具"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            # 构建工具信息
            tool_info = []
            for tool_name in available_tools:
                tool_desc = self.get_tool_description(tool_name)
                if tool_desc:
                    tool_info.append(f"{tool_name}: {tool_desc.description}")
            
            tool_summary = "\n".join(tool_info)
            
            async def get_recommendations():
                async with DeepSeekClient() as llm_client:
                    system_prompt = """You are a tool selection expert. Given a task and available tools, recommend the most appropriate tools.

Consider:
1. Task requirements and complexity
2. Tool capabilities and limitations
3. Tool reliability and performance
4. Tool combination effectiveness

Select 1-3 most suitable tools. Respond with ONLY tool names separated by commas, no additional text."""

                    prompt = f"""Task: {task_description}

Available Tools:
{tool_summary}

Recommend the best tools for this task:"""

                    result = await llm_client.generate_response(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=0.2,
                        max_tokens=100
                    )
                    
                    if result["success"]:
                        recommended_tools = [tool.strip() for tool in result["content"].split(",")]
                        # 验证推荐的工具是否在可用列表中
                        valid_tools = [tool for tool in recommended_tools if tool in available_tools]
                        return valid_tools
                    else:
                        return []
            
            # 由于这是同步方法，我们需要使用同步方式调用
            # 智能简化处理，基于工具性能进行推荐
            if not available_tools:
                return []
            
            # 获取工具性能数据
            tool_performance = self.get_tool_performance_report()
            tools_data = tool_performance.get("tools", [])
            
            # 按成功率排序工具
            sorted_tools = []
            for tool_name in available_tools:
                tool_stats = next((t for t in tools_data if t['tool_name'] == tool_name), None)
                if tool_stats:
                    sorted_tools.append((tool_name, tool_stats['success_rate']))
                else:
                    sorted_tools.append((tool_name, 0.5))  # 默认成功率
            
            # 按成功率降序排序
            sorted_tools.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前3个最佳工具
            recommended_tools = [tool[0] for tool in sorted_tools[:3]]
            
            logging.info(f"Fallback tool recommendation: {recommended_tools}")
            return recommended_tools
            
        except Exception as e:
            logging.error(f"LLM tool recommendation failed: {e}")
            return available_tools[:2] if available_tools else []

    async def get_llm_recommendations(self, task_description: str) -> Dict[str, Any]:
        """使用 LLM 获取智能推荐"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            # 获取工具性能数据
            tool_performance = self.get_tool_performance_report()
            tools_data = tool_performance.get("tools", [])
            
            # 构建工具信息
            tool_info = []
            for tool in tools_data:
                tool_info.append(f"{tool['tool_name']}: {tool['usage_count']} uses, {tool['success_rate']:.1%} success rate")
            
            tool_summary = "\n".join(tool_info) if tool_info else "No tool performance data available"
            
            async with DeepSeekClient() as llm_client:
                system_prompt = """You are an AI agent performance optimization expert. Analyze the task and tool performance data to provide intelligent recommendations.

Consider:
1. Task complexity and requirements
2. Tool performance history and success rates
3. Tool usage patterns and efficiency
4. Potential tool combinations for better results

Provide recommendations in JSON format:
{
    "recommended_tools": ["tool1", "tool2"],
    "avoid_tools": ["tool3"],
    "reasoning": "Explanation for recommendations",
    "estimated_success_probability": 0.85,
    "suggested_approach": "Recommended execution strategy"
}"""

                prompt = f"""Task: {task_description}

Tool Performance Data:
{tool_summary}

Please provide intelligent recommendations for this task:"""

                result = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=300
                )
                
                if result["success"]:
                    try:
                        import json
                        recommendations = json.loads(result["content"])
                        return recommendations
                    except json.JSONDecodeError:
                        logging.warning("Failed to parse LLM recommendations")
                        return self._fallback_recommendations(task_description)
                else:
                    return self._fallback_recommendations(task_description)
                    
        except Exception as e:
            logging.error(f"LLM recommendations failed: {e}")
            return self._fallback_recommendations(task_description)
    
    def _fallback_recommendations(self, task_description: str) -> Dict[str, Any]:
        """回退推荐方法"""
        return {
            "recommended_tools": [],
            "avoid_tools": [],
            "reasoning": "Using fallback recommendation method",
            "estimated_success_probability": 0.5,
            "suggested_approach": "Standard execution approach"
        }


# 全局自适应学习系统实例
adaptive_learning = AdaptiveLearningSystem() 