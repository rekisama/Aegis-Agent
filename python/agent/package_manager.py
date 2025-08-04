#!/usr/bin/env python3
"""
包管理器模块
专门处理Python包的安装，避免使用terminal工具触发服务器重启
"""

import subprocess
import sys
import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

class PackageManager:
    """包管理器，专门处理Python包安装"""
    
    def __init__(self, auto_install_enabled: bool = True):
        self.auto_install_enabled = auto_install_enabled
        self.installed_packages = set()
        self._load_installed_packages()
    
    def _load_installed_packages(self):
        """加载已安装的包列表"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('Package'):
                        package_name = line.split()[0].lower()
                        self.installed_packages.add(package_name)
        except Exception as e:
            logging.warning(f"Failed to load installed packages: {e}")
    
    def set_auto_install_enabled(self, enabled: bool):
        """设置是否启用自动安装"""
        self.auto_install_enabled = enabled
        logging.info(f"自动包安装已{'启用' if enabled else '禁用'}")
    
    async def install_package(self, package_name: str, quiet: bool = True) -> Dict[str, Any]:
        """
        安装Python包
        
        Args:
            package_name: 包名
            quiet: 是否静默安装
            
        Returns:
            安装结果字典
        """
        # 检查是否启用自动安装
        if not self.auto_install_enabled:
            return {
                "success": False,
                "error": "自动包安装已禁用",
                "suggestion": "请手动安装包或启用自动安装功能"
            }
        
        try:
            # 检查是否已安装
            if package_name.lower() in self.installed_packages:
                return {
                    "success": True,
                    "message": f"包 {package_name} 已安装",
                    "already_installed": True
                }
            
            logging.info(f"开始安装包: {package_name}")
            
            # 构建安装命令
            cmd = [sys.executable, "-m", "pip", "install"]
            if quiet:
                cmd.append("--quiet")
            cmd.append(package_name)
            
            # 执行安装
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if process.returncode == 0:
                # 安装成功，更新已安装包列表
                self.installed_packages.add(package_name.lower())
                logging.info(f"包 {package_name} 安装成功")
                return {
                    "success": True,
                    "message": f"包 {package_name} 安装成功",
                    "stdout": stdout.decode('utf-8', errors='ignore'),
                    "stderr": stderr.decode('utf-8', errors='ignore')
                }
            else:
                error_msg = stderr.decode('utf-8', errors='ignore')
                logging.error(f"包 {package_name} 安装失败: {error_msg}")
                return {
                    "success": False,
                    "error": f"安装失败: {error_msg}",
                    "stdout": stdout.decode('utf-8', errors='ignore'),
                    "stderr": error_msg
                }
                
        except asyncio.TimeoutError:
            logging.error(f"包 {package_name} 安装超时")
            return {
                "success": False,
                "error": "安装超时"
            }
        except Exception as e:
            logging.error(f"安装包 {package_name} 时发生错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def install_packages(self, package_list: list, quiet: bool = True) -> Dict[str, Any]:
        """
        批量安装包
        
        Args:
            package_list: 包名列表
            quiet: 是否静默安装
            
        Returns:
            安装结果字典
        """
        # 检查是否启用自动安装
        if not self.auto_install_enabled:
            return {
                "success": False,
                "error": "自动包安装已禁用",
                "suggestion": "请手动安装包或启用自动安装功能"
            }
        
        results = []
        success_count = 0
        
        for package in package_list:
            result = await self.install_package(package, quiet)
            results.append(result)
            if result["success"]:
                success_count += 1
        
        return {
            "success": success_count == len(package_list),
            "total": len(package_list),
            "successful": success_count,
            "failed": len(package_list) - success_count,
            "results": results
        }
    
    def is_package_installed(self, package_name: str) -> bool:
        """检查包是否已安装"""
        return package_name.lower() in self.installed_packages
    
    def get_installed_packages(self) -> set:
        """获取已安装的包列表"""
        return self.installed_packages.copy()
    
    async def check_and_install_package(self, package_name: str) -> Dict[str, Any]:
        """
        检查包是否安装，如果未安装则自动安装
        
        Args:
            package_name: 包名
            
        Returns:
            检查和安装结果
        """
        if self.is_package_installed(package_name):
            return {
                "success": True,
                "message": f"包 {package_name} 已安装",
                "already_installed": True
            }
        
        return await self.install_package(package_name) 