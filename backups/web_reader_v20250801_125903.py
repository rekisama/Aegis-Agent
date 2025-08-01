    async def execute(self, **kwargs) -> ToolResult:
        """
        获取网页内容并提取信息
        
        Args:
            url: 要访问的URL
            extract_title: 是否提取标题
            extract_text: 是否提取文本内容
            timeout: 超时时间（秒）
            
        Returns:
            ToolResult with webpage content
        """
        try:
            url = kwargs.get("url", "")
            extract_title = kwargs.get("extract_title", True)
            extract_text = kwargs.get("extract_text", False)
            timeout = kwargs.get("timeout", 30)
            
            if not url:
                return ToolResult(
                    success=False,
                    data=None,
                    error="No URL provided",
                    metadata={"tool_type": "web_reader"}
                )
            
            # 验证URL格式
            try:
                parsed_url = urlparse(url)
                if not parsed_url.scheme:
                    url = "https://" + url
            except Exception as e:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Invalid URL format: {e}",
                    metadata={"tool_type": "web_reader"}
                )
            
            logging.info(f"Fetching webpage: {url}")
            
            # 创建HTTP会话
            if not self.session:
                timeout_config = aiohttp.ClientTimeout(total=timeout)
                self.session = aiohttp.ClientSession(timeout=timeout_config)
            
            # 发送HTTP请求
            async with self.session.get(url) as response:
                if response.status != 200:
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status}: {response.reason}",
                        metadata={"tool_type": "web_reader", "status_code": response.status}
                    )
                
                # 读取内容
                content = await response.text()
                
                # 提取信息
                result_data = {
                    "url": url,
                    "status_code": response.status,
                    "content_length": len(content),
                    "content_type": response.headers.get("content-type", "unknown")
                }
                
                # 提取标题
                if extract_title:
                    title = self._extract_title(content)
                    result_data["title"] = title
                
                # 提取文本内容
                if extract_text:
                    text = self._extract_text(content)
                    result_data["text"] = text[:1000] + "..." if len(text) > 1000 else text
                
                logging.info(f"Successfully fetched webpage: {url}")
                return ToolResult(
                    success=True,
                    data=result_data,
                    metadata={
                        "tool_type": "web_reader",
                        "url": url,
                        "status_code": response.status
                    }
                )
                
        except asyncio.TimeoutError:
            logging.error(f"Request timeout: {url}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Request timeout after {timeout} seconds",
                metadata={"tool_type": "web_reader", "timeout": True}
            )
        except Exception as e:
            logging.error(f"Failed to fetch webpage: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to fetch webpage: {str(e)}",
                metadata={"tool_type": "web_reader"}
            )
