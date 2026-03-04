"""AI 服务：调用 LLM API"""
import os
import logging
import asyncio
import httpx
import json
import base64
import uuid
from pathlib import Path
from typing import Optional, Tuple, List, Dict, AsyncGenerator
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    """AI 服务客户端"""
    
    def __init__(self):
        """初始化 AI 服务（使用默认配置）"""
        self.default_client, self.default_model_name = self._get_ai_client()
    
    def _get_ai_client(self, model_config: Optional[str] = None) -> Tuple[Optional[OpenAI], str]:
        """
        根据配置获取 OpenAI 兼容的客户端实例和模型名称。
        支持 OpenAI, DeepSeek, Kimi 等兼容 OpenAI 协议的模型。
        
        Args:
            model_config: 模型配置字符串，格式：provider:model_name（如 "deepseek:deepseek-coder"）
                         如果为 None，使用环境变量中的默认配置
        
        Returns:
            (client, model_name) 元组
        """
        # 解析 model_config
        if model_config and ":" in model_config:
            provider, model_name = model_config.split(":", 1)
            provider = provider.lower()
            logger.info(f"使用工具指定的模型配置: {provider}:{model_name}")
        else:
            # 使用默认配置
            provider = os.getenv("CURRENT_PROVIDER", "deepseek").lower()
            model_name = None  # 稍后从环境变量读取
            if model_config:
                logger.warning(f"模型配置格式错误: {model_config}，使用默认配置")
            else:
                logger.info(f"使用系统默认配置: {provider}")
        
        api_key = ""
        base_url = ""
        
        # 根据服务商读取对应的环境变量
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            if not model_name:  # 如果没有指定具体模型，使用默认
                model_name = os.getenv("OPENAI_MODEL", "gpt-4")
        elif provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            if not model_name:
                model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        elif provider == "kimi":
            api_key = os.getenv("KIMI_API_KEY")
            base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
            if not model_name:
                model_name = os.getenv("KIMI_MODEL", "moonshot-v1-8k")
        elif provider == "glm":
            api_key = os.getenv("GLM_API_KEY")
            base_url = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
            if not model_name:
                model_name = os.getenv("GLM_MODEL", "glm-4")
        else:
            logger.warning(f"未知的服务商 [{provider}]，将使用 Mock 模式。")
            return None, "mock-model"
        
        # 校验 API Key 是否有效
        if not api_key or not api_key.startswith("sk-"):
            logger.warning(f"未找到服务商 [{provider}] 的有效 Key，将使用 Mock 模式。")
            return None, "mock-model"
        
        # 从环境变量读取超时配置（秒），默认120秒
        timeout_seconds = float(os.getenv("AI_REQUEST_TIMEOUT", "120"))
        
        # 创建客户端，配置超时时间
        # timeout参数可以是单个数字（所有操作的超时时间）或httpx.Timeout对象（分别配置连接、读取等超时）
        client = OpenAI(
            api_key=api_key, 
            base_url=base_url,
            timeout=timeout_seconds,  # 设置超时时间
            max_retries=2  # 失败后最多重试2次
        )
        
        logger.info(f"AI 客户端初始化成功 - 服务商: {provider}, 模型: {model_name}, 超时: {timeout_seconds}秒")
        return client, model_name
    
    async def generate_welcome_message(self, system_prompt: str, model_config: Optional[str] = None) -> str:
        """
        生成欢迎消息
        
        Args:
            system_prompt: Agent 的系统提示词
            model_config: 模型配置（格式：provider:model_name），如果为 None 使用默认配置
            
        Returns:
            AI 生成的欢迎消息
        """
        # 获取客户端和模型
        client, model_name = self._get_ai_client(model_config) if model_config else (self.default_client, self.default_model_name)
        
        # 无客户端时的模拟返回（用于本地无网调试）
        if not client:
            return "你好！我是你的 AI 助手。请告诉我你需要什么帮助。"
        
        try:
            # 记录系统提示词（用于调试）
            logger.info(f"生成欢迎消息 - 系统提示词长度: {len(system_prompt)} 字符, 使用模型: {model_name}")
            logger.debug(f"系统提示词内容: {system_prompt[:200]}...")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "请用一句话介绍你自己，并询问用户需要什么帮助。"}
                ],
                temperature=0.7
            )
            result = response.choices[0].message.content
            logger.info(f"AI 返回的欢迎消息: {result[:100]}...")
            return result
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"AI 服务调用异常（生成欢迎消息）- 错误类型: {error_type}: {e}", exc_info=True)
            
            # 根据错误类型返回友好提示
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                return "⚠️ AI服务响应超时，请检查网络连接后重试。"
            else:
                return "欢迎使用 AI 助手！抱歉，当前服务暂时不可用，请稍后重试。"
    
    def _find_html_end_position(self, content: str) -> int:
        """
        找到 HTML 文档的结束位置（</html> 标签的位置）
        
        Returns:
            如果找到 </html>，返回其结束位置（包含 </html> 标签）
            如果没找到，返回 -1
        """
        import re
        # 查找最后一个 </html> 标签（不区分大小写）
        pattern = re.compile(r'</html>', re.IGNORECASE)
        matches = list(pattern.finditer(content))
        if matches:
            # 返回最后一个 </html> 标签的结束位置
            last_match = matches[-1]
            return last_match.end()
        return -1
    
    def _detect_content_duplication(self, original: str, continuation: str, threshold: float = 0.7) -> tuple[bool, int]:
        """
        检测继续内容是否与原始内容重复
        
        Args:
            original: 原始内容
            continuation: 继续生成的内容
            threshold: 相似度阈值（0-1）
        
        Returns:
            (is_duplicate, overlap_length)
            is_duplicate: 是否重复
            overlap_length: 重复的长度（如果重复）
        """
        if not continuation or len(continuation) < 50:
            return False, 0
        
        # 方法1：检查继续内容是否在原始内容中出现过（完全匹配）
        # 如果继续内容的前100个字符在原始内容中出现，可能是重复
        continuation_start = continuation[:200].strip()
        if continuation_start in original:
            overlap_pos = original.find(continuation_start)
            if overlap_pos >= 0:
                # 计算重复的长度
                overlap_length = min(len(continuation_start), len(original) - overlap_pos)
                logger.warning(f"检测到继续内容在原始内容中完全匹配，位置: {overlap_pos}, 重复长度: {overlap_length}")
                return True, overlap_length
        
        # 方法2：检查继续内容是否与原始内容的结尾高度相似
        # 比较原始内容的最后 N 个字符与继续内容的前 N 个字符
        compare_length = min(300, len(original), len(continuation))
        if compare_length < 50:
            return False, 0
        
        original_end = original[-compare_length:].lower().strip()
        continuation_start = continuation[:compare_length].lower().strip()
        
        # 计算相似度
        same_chars = sum(1 for a, b in zip(original_end, continuation_start) if a == b)
        similarity = same_chars / compare_length if compare_length > 0 else 0
        
        if similarity >= threshold:
            # 找到最佳分割点
            split_pos = 0
            for i in range(min(len(original_end), len(continuation_start)) - 1, -1, -1):
                if original_end[i] != continuation_start[i]:
                    split_pos = i + 1
                    break
            if split_pos > 0:
                logger.warning(f"检测到高相似度重复（{similarity:.2%}），建议去除前 {split_pos} 字符")
                return True, split_pos
        
        return False, 0
    
    def _clean_after_html_end(self, content: str) -> str:
        """
        清理 </html> 标签之后的内容
        
        如果检测到 </html> 标签，只保留到 </html> 标签结束的内容
        """
        html_end_pos = self._find_html_end_position(content)
        if html_end_pos > 0:
            # 检查 </html> 之后是否有内容
            after_html = content[html_end_pos:].strip()
            if after_html:
                logger.warning(f"检测到 </html> 标签之后还有内容（{len(after_html)} 字符），将清理掉")
                logger.debug(f"</html> 之后的内容预览（前200字符）:\n{after_html[:200]}")
                # 只保留到 </html> 标签结束
                return content[:html_end_pos].rstrip()
        return content
    
    def _check_code_completeness(self, content: str) -> dict:
        """
        检测代码完整性（HTML/JavaScript）
        
        Returns:
            {
                'is_complete': bool,
                'missing_tags': list,  # 缺失的闭合标签
                'issues': list  # 其他问题
            }
        """
        import re
        issues = []
        missing_tags = []
        
        content_lower = content.lower()
        is_html = '<html' in content_lower or '<!doctype' in content_lower
        
        if is_html:
            # 检查 HTML 标签匹配
            html_open = content_lower.count('<html')
            html_close = content_lower.count('</html>')
            if html_open > html_close:
                missing_tags.append('</html>')
                issues.append(f'HTML标签不匹配: <html>={html_open}, </html>={html_close}')
            
            body_open = content_lower.count('<body')
            body_close = content_lower.count('</body>')
            if body_open > body_close:
                missing_tags.append('</body>')
                issues.append(f'Body标签不匹配: <body>={body_open}, </body>={body_close}')
            
            head_open = content_lower.count('<head')
            head_close = content_lower.count('</head>')
            if head_open > head_close:
                missing_tags.append('</head>')
                issues.append(f'Head标签不匹配: <head>={head_open}, </head>={head_close}')
            
            # 检查未闭合的标签（简单检测）
            # 查找所有开始标签，检查是否有对应的结束标签
            tag_pattern = re.compile(r'<(\w+)[^>]*>', re.IGNORECASE)
            open_tags = tag_pattern.findall(content)
            close_tag_pattern = re.compile(r'</(\w+)>', re.IGNORECASE)
            close_tags = close_tag_pattern.findall(content)
            
            # 统计标签（忽略自闭合标签）
            self_closing_tags = {'br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
            tag_counts = {}
            for tag in open_tags:
                if tag.lower() not in self_closing_tags:
                    tag_counts[tag.lower()] = tag_counts.get(tag.lower(), 0) + 1
            for tag in close_tags:
                if tag.lower() in tag_counts:
                    tag_counts[tag.lower()] -= 1
            
            # 找出未闭合的标签
            for tag, count in tag_counts.items():
                if count > 0:
                    issues.append(f'未闭合的标签: <{tag}> (缺少 {count} 个闭合标签)')
        
        # 检查 JavaScript 括号匹配（简单检测）
        if '<script' in content_lower:
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces > close_braces:
                issues.append(f'JavaScript大括号不匹配: {{={open_braces}, }}={close_braces}')
            
            open_parens = content.count('(')
            close_parens = content.count(')')
            if open_parens > close_parens:
                issues.append(f'JavaScript圆括号不匹配: (={open_parens}, )={close_parens}')
        
        # 检查 HTML 是否已经完整闭合（有 </html> 标签）
        html_end_pos = self._find_html_end_position(content)
        if is_html and html_end_pos > 0:
            # 检查 </html> 之后是否有有效内容
            after_html = content[html_end_pos:].strip()
            # 如果 </html> 之后只有空白或很少的内容，认为 HTML 已经完整
            if len(after_html) < 50 or not any(c.isalnum() for c in after_html):
                # HTML 已经完整闭合
                is_complete = True
                logger.info("HTML 已经完整闭合（检测到 </html> 标签且之后无有效内容）")
            else:
                # </html> 之后还有内容，可能是重复或错误
                issues.append(f'</html> 标签之后还有内容（{len(after_html)} 字符），可能是重复内容')
                is_complete = False
        else:
            is_complete = len(issues) == 0
        
        return {
            'is_complete': is_complete,
            'missing_tags': missing_tags,
            'issues': issues,
            'html_end_pos': html_end_pos if is_html else -1
        }
    
    def _clean_continue_result(self, continue_result: str, is_html: bool = False) -> str:
        """
        清理自动继续返回的内容，提取纯代码内容
        
        处理情况：
        1. 如果包含Markdown代码块标记（```html、```等），提取代码块内的内容
        2. 清理对话文本、注释等非代码内容
        3. 处理可能的重复标记
        
        Args:
            continue_result: AI继续返回的原始内容
            is_html: 是否是HTML内容
            
        Returns:
            清理后的纯代码内容
        """
        import re
        
        result = continue_result.strip()
        
        # 1. 尝试提取Markdown代码块内的内容
        # 匹配 ```语言标记\n内容\n``` 格式
        code_block_pattern = re.compile(r'```(?:\w+)?\s*\n(.*?)```', re.DOTALL)
        matches = code_block_pattern.findall(result)
        if matches:
            # 如果找到代码块，使用最后一个代码块的内容（AI可能输出多个代码块）
            extracted_content = matches[-1].strip()
            logger.info(f"从Markdown代码块中提取内容，原始长度: {len(result)}, 提取后长度: {len(extracted_content)}")
            result = extracted_content
        
        # 2. 清理常见的对话文本和注释
        # 移除类似 "当然,这里是完成的HTML代码:" 这样的对话文本
        # 移除类似 "// ... 省略已生成部分 ..." 这样的注释
        lines = result.split('\n')
        cleaned_lines = []
        skip_patterns = [
            r'^当然[,，].*',
            r'^这里是.*',
            r'^以下是.*',
            r'^//\s*\.\.\.\s*.*',
            r'^//\s*省略.*',
            r'^#\s*\.\.\.\s*.*',
            r'^#\s*省略.*',
        ]
        
        for line in lines:
            # 跳过匹配对话文本模式的行
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    should_skip = True
                    logger.debug(f"跳过对话文本行: {line[:100]}")
                    break
            if not should_skip:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines).strip()
        
        # 3. 如果是HTML，确保没有残留的Markdown标记
        if is_html:
            # 移除可能的残留标记
            result = re.sub(r'^```\s*\w*\s*\n', '', result, flags=re.MULTILINE)
            result = re.sub(r'\n```\s*$', '', result, flags=re.MULTILINE)
            result = result.strip()
        
        logger.info(f"清理完成，最终内容长度: {len(result)} 字符")
        if len(result) != len(continue_result):
            logger.info(f"清理前后对比预览（清理后前200字符）:\n{result[:200]}")
        
        return result
    
    async def chat(self, system_prompt: str, history: List[Dict[str, str]], user_message: str, max_continue: int = 3, model_config: Optional[str] = None) -> str:
        """
        进行对话（非流式）
        
        Args:
            system_prompt: Agent 的系统提示词
            history: 历史消息列表（格式：[{"role": "user/assistant", "content": "..."}, ...]）
            user_message: 用户当前消息
            max_continue: 最大继续生成次数（防止无限递归）
            model_config: 模型配置（格式：provider:model_name），如果为 None 使用默认配置
            
        Returns:
            AI 生成的回复
        """
        # 获取客户端和模型
        client, model_name = self._get_ai_client(model_config) if model_config else (self.default_client, self.default_model_name)
        
        # 无客户端时的模拟返回
        if not client:
            return f"Mock 回复：收到你的消息「{user_message}」"
        
        try:
            # 构建消息链：System Prompt + History + Current Input
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史消息
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 记录系统提示词（用于调试）
            logger.info(f"对话请求 - 系统提示词长度: {len(system_prompt)} 字符, 历史消息数: {len(history)}, 用户消息: {user_message[:50]}..., 使用模型: {model_name}")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            logger.info(f"AI 返回的回复长度: {len(result)} 字符, finish_reason: {finish_reason}")
            
            # 如果内容包含HTML，记录详细信息用于排查
            if '<html' in result.lower() or '<!doctype' in result.lower():
                logger.info("=" * 80)
                logger.info("检测到HTML内容，记录详细信息用于排查:")
                logger.info(f"HTML内容长度: {len(result)} 字符")
                logger.info(f"包含 <html> 标签: {'<html' in result.lower()}")
                logger.info(f"包含 </html> 标签: {'</html>' in result.lower()}")
                logger.info(f"包含 <!doctype> 标签: {'<!doctype' in result.lower()}")
                logger.info(f"HTML内容预览（前1000字符）:\n{result[:1000]}")
                logger.info(f"HTML内容预览（后1000字符）:\n{result[-1000:]}")
                # 检查HTML标签是否完整
                html_open_count = result.lower().count('<html')
                html_close_count = result.lower().count('</html>')
                body_open_count = result.lower().count('<body')
                body_close_count = result.lower().count('</body>')
                logger.info(f"HTML标签统计: <html>={html_open_count}, </html>={html_close_count}, <body>={body_open_count}, </body>={body_close_count}")
                if html_open_count != html_close_count:
                    logger.warning(f"⚠️ HTML标签不匹配！<html>标签数: {html_open_count}, </html>标签数: {html_close_count}")
                logger.info("=" * 80)
            
            # 如果因为达到最大token限制而截断，自动继续生成直到完整
            if finish_reason == 'length' and max_continue > 0:
                logger.info(f"检测到内容因token限制被截断，开始自动继续生成（剩余次数: {max_continue}，内容长度: {len(result)}）...")
                
                # 循环继续生成，直到代码完整或达到最大次数
                accumulated_result = result
                continue_count = 0
                is_html = '<html' in result.lower() or '<!doctype' in result.lower()
                
                while max_continue > 0:
                    continue_count += 1
                    logger.info(f"第 {continue_count} 次继续生成（剩余次数: {max_continue}）...")
                    logger.info(f"当前内容长度: {len(accumulated_result)} 字符")
                    logger.info(f"截断位置预览（最后500字符）:\n{accumulated_result[-500:]}")
                    
                    # 清理 </html> 之后的内容（如果存在）
                    if is_html:
                        accumulated_result = self._clean_after_html_end(accumulated_result)
                    
                    # 检查代码完整性
                    completeness_check = self._check_code_completeness(accumulated_result)
                    if completeness_check['is_complete']:
                        logger.info("✅ 代码完整性检查通过，停止继续生成")
                        break
                    else:
                        logger.warning(f"⚠️ 代码不完整，问题: {completeness_check['issues']}")
                        if completeness_check['missing_tags']:
                            logger.warning(f"缺失的标签: {completeness_check['missing_tags']}")
                        
                        # 如果 HTML 已经有 </html> 标签，但检测到不完整，可能是检测逻辑问题
                        # 这种情况下，如果 </html> 之后没有内容，应该认为完整
                        if is_html and completeness_check['html_end_pos'] > 0:
                            after_html = accumulated_result[completeness_check['html_end_pos']:].strip()
                            if len(after_html) < 50:
                                logger.info("HTML 已完整闭合，停止继续生成")
                                break
                    
                    # 生成继续提示词（更严格的提示）
                    if is_html:
                        # 检查是否已经有 </html> 标签
                        if completeness_check['html_end_pos'] > 0:
                            # 已经有 </html>，不应该继续生成
                            logger.warning("检测到 HTML 已有 </html> 标签，但完整性检查未通过，可能是检测逻辑问题")
                            # 检查 </html> 之后的内容
                            after_html = accumulated_result[completeness_check['html_end_pos']:].strip()
                            if len(after_html) < 50:
                                # </html> 之后没有有效内容，认为完整
                                break
                            else:
                                # </html> 之后有内容，可能是重复，清理掉后停止
                                accumulated_result = accumulated_result[:completeness_check['html_end_pos']].rstrip()
                                break
                        
                        if completeness_check['missing_tags']:
                            missing_tags_str = '、'.join(completeness_check['missing_tags'])
                            continue_message = f"上面的HTML代码被截断了，请继续完成剩余的HTML代码。需要确保包含以下缺失的标签: {missing_tags_str}。重要：只输出HTML代码内容，不要包含Markdown代码块标记（```html或```），不要包含任何解释文字或注释，不要重复已生成的部分，直接继续输出HTML代码。"
                        else:
                            continue_message = "上面的HTML代码被截断了，请继续完成剩余的内容。重要：只输出HTML代码内容，不要包含Markdown代码块标记（```html或```），不要包含任何解释文字或注释，不要重复已生成的部分，直接继续输出HTML代码。如果HTML已经完整（已有</html>标签），请停止输出。"
                    else:
                        continue_message = "请继续完成上面的内容，不要重复已生成的部分。如果内容是代码，请只输出代码内容，不要包含Markdown代码块标记或解释文字。"
                    
                    # 将已生成的内容添加到历史消息中
                    new_history = history + [
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": accumulated_result}
                    ]
                    
                    # 继续生成（传递 model_config）
                    continue_result = await self.chat(system_prompt, new_history, continue_message, max_continue - 1, model_config)
                    
                    # 清理继续返回的内容
                    cleaned_continue_result = self._clean_continue_result(continue_result, is_html)
                    
                    if not cleaned_continue_result or len(cleaned_continue_result.strip()) == 0:
                        logger.warning("继续生成的内容为空，停止继续")
                        break
                    
                    # 检测内容重复（更严格的检测）
                    is_duplicate, overlap_length = self._detect_content_duplication(
                        accumulated_result, 
                        cleaned_continue_result,
                        threshold=0.6  # 降低阈值，更严格检测重复
                    )
                    
                    if is_duplicate:
                        if overlap_length > 0:
                            # 去除重复部分
                            cleaned_continue_result = cleaned_continue_result[overlap_length:]
                            logger.warning(f"检测到内容重复，去除前 {overlap_length} 字符")
                        
                        # 如果去除重复后内容很少或为空，可能是完全重复
                        if len(cleaned_continue_result.strip()) < 100:
                            logger.warning("继续生成的内容与原始内容高度重复，停止继续生成")
                            break
                    
                    # 如果 HTML 已经有 </html> 标签，检查继续内容是否应该被忽略
                    if is_html and completeness_check['html_end_pos'] > 0:
                        # HTML 已经完整，继续生成的内容可能是重复的
                        # 检查继续内容是否包含 </html> 或重复的代码结构
                        if '</html>' in cleaned_continue_result.lower():
                            logger.warning("继续生成的内容包含 </html> 标签，但原始内容已有 </html>，可能是重复，忽略继续内容")
                            break
                        
                        # 检查继续内容是否与原始内容的某部分重复
                        # 如果继续内容的前200字符在原始内容中出现过，可能是重复
                        continue_preview = cleaned_continue_result[:200].strip()
                        if continue_preview in accumulated_result:
                            logger.warning("继续生成的内容与原始内容重复，忽略继续内容")
                            break
                    
                    # 拼接结果
                    accumulated_result = accumulated_result + cleaned_continue_result
                    
                    # 再次清理 </html> 之后的内容（防止拼接后出现问题）
                    if is_html:
                        accumulated_result = self._clean_after_html_end(accumulated_result)
                    
                    max_continue -= 1
                    
                    logger.info(f"第 {continue_count} 次继续完成，当前总长度: {len(accumulated_result)} 字符（本次新增: {len(cleaned_continue_result)} 字符）")
                
                # 最终清理和验证
                if is_html:
                    accumulated_result = self._clean_after_html_end(accumulated_result)
                
                # 最终完整性检查
                final_check = self._check_code_completeness(accumulated_result)
                if not final_check['is_complete']:
                    logger.warning(f"⚠️ 经过 {continue_count} 次继续生成后，代码仍然不完整:")
                    for issue in final_check['issues']:
                        logger.warning(f"  - {issue}")
                else:
                    logger.info(f"✅ 经过 {continue_count} 次继续生成，代码已完整")
                
                # 记录最终结果
                if is_html:
                    logger.info("=" * 80)
                    logger.info("最终HTML内容检查:")
                    logger.info(f"最终内容长度: {len(accumulated_result)} 字符")
                    logger.info(f"包含 <html> 标签: {'<html' in accumulated_result.lower()}")
                    logger.info(f"包含 </html> 标签: {'</html>' in accumulated_result.lower()}")
                    logger.info("=" * 80)
                
                return accumulated_result
            
            return result
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"AI 服务调用异常（对话）- 错误类型: {error_type}: {e}", exc_info=True)
            
            # 根据错误类型返回友好提示
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                return "⚠️ AI服务响应超时，可能是网络问题，请稍后重试。"
            elif "connection" in str(e).lower():
                return "⚠️ 无法连接到AI服务，请检查网络或API配置。"
            else:
                return f"⚠️ AI服务调用失败: {str(e)[:100]}"
    
    async def chat_stream(self, system_prompt: str, history: List[Dict[str, str]], user_message: str, max_continue: int = 3, model_config: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        进行对话（流式输出）
        
        Args:
            system_prompt: Agent 的系统提示词
            history: 历史消息列表（格式：[{"role": "user/assistant", "content": "..."}, ...]）
            user_message: 用户当前消息
            max_continue: 最大继续生成次数（防止无限递归）
            model_config: 模型配置（格式：provider:model_name），如果为 None 使用默认配置
            
        Yields:
            str: AI 生成的回复片段（逐块返回）
        """
        # 获取客户端和模型
        client, model_name = self._get_ai_client(model_config) if model_config else (self.default_client, self.default_model_name)
        
        # 无客户端时的模拟返回
        if not client:
            mock_reply = f"Mock 回复：收到你的消息「{user_message}」"
            # 模拟流式输出
            for char in mock_reply:
                yield char
                await asyncio.sleep(0.05)  # 模拟延迟
            return
        
        try:
            # 构建消息链：System Prompt + History + Current Input
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史消息
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 记录系统提示词（用于调试）
            logger.info(f"流式对话请求 - 系统提示词长度: {len(system_prompt)} 字符, 历史消息数: {len(history)}, 用户消息: {user_message[:50]}..., 使用模型: {model_name}")
            
            # 使用流式输出（同步调用，需要在异步函数中处理）
            # 注意：OpenAI 客户端的流式调用是同步的，需要在异步上下文中处理
            stream = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                stream=True  # 启用流式输出
            )
            
            # 逐块返回内容（在异步上下文中处理同步流）
            accumulated_content = ""
            finish_reason = None
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    delta = choice.delta
                    if delta and delta.content:
                        accumulated_content += delta.content
                        yield delta.content
                        # 让出控制权，允许其他协程运行，确保流式数据及时发送
                        await asyncio.sleep(0.001)  # 很小的延迟，确保流式效果
                    
                    # 检查是否完成，并记录 finish_reason
                    if choice.finish_reason:
                        finish_reason = choice.finish_reason
                        logger.info(f"流式输出完成，finish_reason: {finish_reason}, 已生成内容长度: {len(accumulated_content)}")
            
            # 如果因为达到最大token限制而截断，判断是否需要自动继续
            # 只有在以下情况才自动继续：
            # 1. finish_reason == 'length'（确实因为token限制截断）
            # 2. 内容长度超过一定阈值（比如1000字符，说明是长内容）
            # 3. 内容包含代码块标记（```），说明是代码生成任务
            # 4. 内容不以问号、感叹号结尾，且不包含明显的追问词（避免干扰多轮对话）
            should_auto_continue = (
                finish_reason == 'length' and 
                max_continue > 0 and
                len(accumulated_content) > 1000 and  # 内容足够长
                ('```' in accumulated_content or '<' in accumulated_content) and  # 包含代码或HTML标记
                not accumulated_content.rstrip().endswith(('?', '？', '!', '！')) and  # 不以问号/感叹号结尾
                not any(word in accumulated_content[-200:] for word in ['请', '需要', '能否', '可以', '希望', '想要'])  # 最后200字符不包含追问词
            )
            
            if should_auto_continue:
                logger.info(f"检测到长内容因token限制被截断，自动继续生成（剩余次数: {max_continue}，内容长度: {len(accumulated_content)}）...")
                logger.debug(f"已生成内容预览（最后500字符）: {accumulated_content[-500:]}")
                
                # 将已生成的内容添加到历史消息中
                new_history = history + [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": accumulated_content}
                ]
                
                # 更明确的续写提示：要求AI不要输出代码块标记
                continue_message = "请继续完成上面的内容。重要：直接输出代码内容，不要包含```标记，不要重复已生成的部分，从上一次截断的地方继续。"
                
                # 用于检测和清理续写内容开头的代码块标记
                continue_buffer = ""
                first_chunk_processed = False
                continue_count = 0
                
                async for chunk in self.chat_stream(system_prompt, new_history, continue_message, max_continue - 1, model_config):
                    if not first_chunk_processed:
                        # 累积前几个chunk，用于检测开头是否有代码块标记
                        continue_buffer += chunk
                        
                        # 当累积了足够的字符时（至少20个字符），进行检测
                        if len(continue_buffer) >= 20:
                            import re
                            # 检测开头是否有 ```语言\n 格式的代码块标记
                            fence_match = re.match(r'^```\w*\s*\n', continue_buffer)
                            if fence_match:
                                # 去除开头的代码块标记
                                continue_buffer = continue_buffer[fence_match.end():]
                                logger.info(f"检测到续写内容开头有代码块标记（{fence_match.group()}），已自动去除")
                            
                            # 输出缓冲区内容
                            if continue_buffer:
                                continue_count += len(continue_buffer)
                                yield continue_buffer
                            
                            # 标记已处理完第一个chunk
                            first_chunk_processed = True
                            continue_buffer = ""
                    else:
                        # 后续chunk直接输出
                        continue_count += len(chunk)
                        yield chunk
                
                # 如果还有剩余的缓冲区内容（累积的字符不足20个），输出
                if continue_buffer:
                    # 对剩余内容也检查一次
                    import re
                    fence_match = re.match(r'^```\w*\s*\n', continue_buffer)
                    if fence_match:
                        continue_buffer = continue_buffer[fence_match.end():]
                        logger.info(f"检测到续写内容开头有代码块标记（短内容），已自动去除")
                    
                    if continue_buffer:
                        continue_count += len(continue_buffer)
                        yield continue_buffer
                
                logger.info(f"自动继续生成完成，继续部分长度: {continue_count} 字符")
            elif finish_reason == 'length':
                logger.info(f"检测到内容因token限制被截断，但判断为AI追问或短内容，不自动继续（内容长度: {len(accumulated_content)}）")
                logger.debug(f"内容预览（最后200字符）: {accumulated_content[-200:]}")
                    
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"AI 服务调用异常（流式对话）- 错误类型: {error_type}: {e}", exc_info=True)
            
            # 根据不同错误类型给出更友好的提示
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                yield "⚠️ AI服务响应超时，可能是网络问题。建议：\n1. 检查网络连接\n2. 如果使用代理，请确认代理设置正确\n3. 稍后重试"
            elif "connection" in str(e).lower() or "connect" in str(e).lower():
                yield "⚠️ 无法连接到AI服务，请检查：\n1. 网络是否正常\n2. API密钥是否正确\n3. 服务提供商是否可用"
            else:
                yield f"⚠️ AI服务调用失败: {str(e)[:100]}\n请稍后重试或联系管理员。"
    
    # ==================== 多模态生成功能 ====================
    
    async def generate_image(
        self,
        prompt: str,
        model_config: str,  # "glm:cogview-4"
        size: str = "1024x1024",
        count: int = 1,
        style: Optional[str] = None
    ) -> Dict[str, any]:
        """
        调用GLM图像生成API（异步）
        
        Args:
            prompt: 图片描述提示词
            model_config: 模型配置（格式：glm:model_name）
            size: 图片尺寸（如 "1024x1024", "512x512"）
            count: 生成数量（1-4）
            style: 生成风格（可选）
        
        Returns:
            {"task_id": "xxx", "request_id": "xxx"}
        
        Raises:
            ValueError: 不支持的服务商或参数错误
            Exception: API调用失败
        """
        # 解析模型配置
        if not model_config or ":" not in model_config:
            raise ValueError(f"模型配置格式错误: {model_config}")
        
        provider, model_name = model_config.split(":", 1)
        provider = provider.lower()
        
        if provider != "glm":
            raise ValueError(f"图像生成仅支持GLM服务商，当前配置: {provider}")
        
        # 获取GLM配置
        api_key = os.getenv("GLM_API_KEY")
        base_url = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        
        if not api_key:
            raise ValueError("未配置GLM_API_KEY")
        
        # 构建请求
        url = f"{base_url}/images/generations"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求体
        payload = {
            "model": model_name,
            "prompt": prompt
        }
        
        # 添加可选参数
        # 注意：GLM API可能不支持所有这些参数，我们需要通过日志观察实际支持的参数
        if size:
            payload["size"] = size
        
        # count 参数：移除 count > 1 的限制，始终传递
        if count:
            payload["n"] = count  # DALL-E风格的参数名
        
        if style:
            payload["style"] = style
        
        try:
            print("\n" + "-"*50)
            print("【调用GLM API】")
            print(f"模型: {model_name}")
            print(f"提示词: {prompt[:100]}...")
            print(f"参数 - size: {size}, count: {count}, style: {style}")
            print(f"完整payload: {payload}")
            print("-"*50 + "\n")
            
            logger.info(f"调用GLM图像生成API - 模型: {model_name}, payload: {payload}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:  # 延长超时到60秒，因为图片生成需要时间
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                print("\n" + "~"*50)
                print("【GLM API 返回结果】")
                print(f"状态码: {response.status_code}")
                print(f"返回数据: {result}")
                print(f"data字段存在: {'data' in result}")
                if "data" in result:
                    print(f"data内容: {result['data']}")
                    print(f"图片数量: {len(result.get('data', []))}")
                print("~"*50 + "\n")
                
                logger.info(f"GLM图像生成API调用成功，完整返回: {result}")
                
                # 检查GLM是否直接返回了图片（同步模式）
                if "data" in result:
                    # 同步模式：{"data": [{"url": "..."}, ...]}
                    print(f"✓ GLM同步模式，返回了 {len(result['data'])} 张图片")
                    logger.info("GLM返回了同步结果（直接包含图片）")
                    return {
                        "mode": "sync",
                        "data": result["data"]
                    }
                else:
                    # 异步模式：{"id": "task_xxx", ...}
                    print(f"✓ GLM异步模式，任务ID: {result.get('id')}")
                    logger.info(f"GLM返回了异步任务ID: {result}")
                    return {
                        "mode": "async",
                        "result": result
                    }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"GLM API返回错误: {e.response.status_code} - {e.response.text}")
            raise Exception(f"图像生成失败: {e.response.text}")
        except httpx.TimeoutException:
            logger.error("GLM API请求超时")
            raise Exception("图像生成请求超时，请稍后重试")
        except Exception as e:
            logger.error(f"GLM图像生成异常: {e}", exc_info=True)
            raise
    
    async def get_image_result(self, task_id: str) -> Dict[str, any]:
        """
        查询GLM图像生成结果
        
        Args:
            task_id: 任务ID
        
        Returns:
            {
                "status": "completed" | "processing" | "failed",
                "data": [{"url": "https://..."}, ...],
                "metadata": {...}
            }
        
        Raises:
            Exception: API调用失败
        """
        api_key = os.getenv("GLM_API_KEY")
        base_url = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        
        if not api_key:
            raise ValueError("未配置GLM_API_KEY")
        
        # 构建请求
        url = f"{base_url}/async-result/{task_id}"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"查询任务状态: {task_id} - {result.get('task_status')} - 完整结果: {result}")
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"GLM查询结果失败: {e.response.status_code} - {e.response.text}")
            raise Exception(f"查询生成结果失败: {e.response.text}")
        except Exception as e:
            logger.error(f"查询GLM任务状态异常: {e}", exc_info=True)
            raise
    
    async def generate_audio(
        self,
        prompt: str,
        model_config: str,
        voice: str = None,
        **kwargs
    ) -> Dict[str, any]:
        """
        生成音频（文本转语音）
        
        Args:
            prompt: 要转换为语音的文本
            model_config: 模型配置（格式：provider:model_name）
            voice: 音色ID（可选）
            **kwargs: 其他参数
        
        Returns:
            {
                "mode": "sync",
                "data": [{"url": "https://..."}, ...],
                "metadata": {...}
            }
        
        Raises:
            Exception: API调用失败
        """
        # 解析模型配置
        if not model_config or ":" not in model_config:
            raise ValueError(f"模型配置格式错误: {model_config}")
        
        provider, model_name = model_config.split(":", 1)
        provider = provider.lower()
        
        if provider != "glm":
            raise ValueError(f"音频生成仅支持GLM服务商，当前配置: {provider}")
        
        # 获取GLM配置
        api_key = os.getenv("GLM_API_KEY")
        base_url = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        
        if not api_key:
            raise ValueError("未配置GLM_API_KEY")
        
        # GLM-TTS需要使用glm-4-voice模型通过chat/completions调用
        # 将glm-tts映射到glm-4-voice
        if model_name == "glm-tts":
            model_name = "glm-4-voice"
        
        # 构建请求 - 使用chat/completions端点
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求体 - GLM-4-Voice的content必须是列表格式
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "stream": False  # 同步调用
        }
        
        try:
            print("\n" + "-"*50)
            print("【调用GLM TTS API】")
            print(f"模型: {model_name}")
            print(f"文本: {prompt[:100]}...")
            print(f"音色: {voice}")
            print(f"完整payload: {payload}")
            print("-"*50 + "\n")
            
            logger.info(f"调用GLM音频生成API - 模型: {model_name}, payload: {payload}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                print("\n" + "~"*50)
                print("【GLM TTS API 返回结果】")
                print(f"状态码: {response.status_code}")
                print(f"返回数据: {result}")
                print("~"*50 + "\n")
                
                logger.info(f"GLM音频生成API调用成功，完整返回: {result}")
                
                # GLM-4-Voice 通过chat/completions返回
                # 返回格式示例: {"choices": [{"message": {"content": "...", "audio": {...}}}]}
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    
                    # 检查是否有音频数据
                    audio_data = message.get("audio")
                    if audio_data and isinstance(audio_data, dict):
                        # 检查是否是URL
                        audio_url = audio_data.get("url")
                        if audio_url:
                            return {
                                "mode": "sync",
                                "data": [{"url": audio_url}]
                            }
                        
                        # 检查是否是base64编码的音频
                        audio_base64 = audio_data.get("data") or audio_data.get("audio")
                        if audio_base64:
                            print(f"检测到base64音频数据，长度: {len(audio_base64)}")
                            
                            # 保存base64音频到文件
                            audio_url = await self._save_base64_audio(audio_base64, audio_data.get("format", "mp3"))
                            
                            return {
                                "mode": "sync",
                                "data": [{"url": audio_url}]
                            }
                    
                    # 如果没有audio字段，可能音频在content中
                    content = message.get("content", "")
                    if content:
                        # TODO: 处理content中可能包含的音频信息
                        logger.warning(f"GLM返回了文本内容而非音频: {content}")
                
                # 尝试其他可能的格式
                if "data" in result:
                    data_obj = result["data"]
                    if isinstance(data_obj, dict):
                        audio_url = data_obj.get("url")
                        if audio_url:
                            return {
                                "mode": "sync",
                                "data": [{"url": audio_url}]
                            }
                
                # 如果都不匹配，抛出异常
                raise Exception(f"无法从GLM响应中提取音频数据，返回格式: {result}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"GLM API返回错误: {e.response.status_code} - {e.response.text}")
            raise Exception(f"音频生成失败: {e.response.text}")
        except httpx.TimeoutException:
            logger.error("GLM API请求超时")
            raise Exception("音频生成请求超时，请稍后重试")
        except Exception as e:
            logger.error(f"GLM音频生成异常: {e}", exc_info=True)
            raise
    
    async def _save_base64_audio(self, base64_data: str, audio_format: str = "mp3") -> str:
        """
        保存base64编码的音频到本地文件
        
        Args:
            base64_data: base64编码的音频数据
            audio_format: 音频格式（mp3, wav等）
        
        Returns:
            可访问的音频URL路径
        """
        try:
            # 创建static/media/audio目录（与HTML上传统一到static目录）
            static_dir = Path(__file__).parent.parent.parent / "static"
            media_dir = static_dir / "media" / "audio"
            media_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成唯一文件名
            file_name = f"{uuid.uuid4()}.{audio_format}"
            file_path = media_dir / file_name
            
            # 解码base64并保存
            audio_bytes = base64.b64decode(base64_data)
            with open(file_path, "wb") as f:
                f.write(audio_bytes)
            
            # 返回可访问的URL（通过/static路径访问）
            audio_url = f"/static/media/audio/{file_name}"
            
            logger.info(f"Base64音频已保存: {file_path}, URL: {audio_url}")
            print(f"✓ Base64音频已保存到: {file_path}")
            print(f"✓ 访问URL: {audio_url}")
            
            return audio_url
            
        except Exception as e:
            logger.error(f"保存base64音频失败: {e}", exc_info=True)
            raise Exception(f"保存音频文件失败: {str(e)}")
    
    async def generate_video(
        self,
        prompt: str,
        model_config: str,
        size: str = None,
        fps: int = None,
        quality: str = None,
        with_audio: bool = False,
        **kwargs
    ) -> Dict[str, any]:
        """
        生成视频（文本转视频）
        
        Args:
            prompt: 视频描述文本
            model_config: 模型配置（格式：provider:model_name）
            size: 视频分辨率（如：1920x1080）
            fps: 帧率（30或60）
            quality: 质量模式（quality或speed）
            with_audio: 是否生成AI音效
            **kwargs: 其他参数
        
        Returns:
            {
                "mode": "async",
                "result": {"id": "task_xxx", ...}
            }
        
        Raises:
            Exception: API调用失败
        """
        # 解析模型配置
        if not model_config or ":" not in model_config:
            raise ValueError(f"模型配置格式错误: {model_config}")
        
        provider, model_name = model_config.split(":", 1)
        provider = provider.lower()
        
        if provider != "glm":
            raise ValueError(f"视频生成仅支持GLM服务商，当前配置: {provider}")
        
        # 获取GLM配置
        api_key = os.getenv("GLM_API_KEY")
        base_url = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        
        if not api_key:
            raise ValueError("未配置GLM_API_KEY")
        
        # 构建请求
        url = f"{base_url}/videos/generations"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求体
        payload = {
            "model": model_name,
            "prompt": prompt
        }
        
        # 添加可选参数
        if size:
            payload["size"] = size
        if fps:
            payload["fps"] = fps
        if quality:
            payload["quality"] = quality
        if with_audio:
            payload["with_audio"] = with_audio
        
        try:
            print("\n" + "-"*50)
            print("【调用GLM Video API】")
            print(f"模型: {model_name}")
            print(f"提示词: {prompt[:100]}...")
            print(f"参数 - size: {size}, fps: {fps}, quality: {quality}, with_audio: {with_audio}")
            print(f"完整payload: {payload}")
            print("-"*50 + "\n")
            
            logger.info(f"调用GLM视频生成API - 模型: {model_name}, payload: {payload}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                print("\n" + "~"*50)
                print("【GLM Video API 返回结果】")
                print(f"状态码: {response.status_code}")
                print(f"返回数据: {result}")
                print("~"*50 + "\n")
                
                logger.info(f"GLM视频生成API调用成功，完整返回: {result}")
                
                # CogVideoX 返回异步任务ID
                return {
                    "mode": "async",
                    "result": result
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"GLM API返回错误: {e.response.status_code} - {e.response.text}")
            raise Exception(f"视频生成失败: {e.response.text}")
        except httpx.TimeoutException:
            logger.error("GLM API请求超时")
            raise Exception("视频生成请求超时，请稍后重试")
        except Exception as e:
            logger.error(f"GLM视频生成异常: {e}", exc_info=True)
            raise
    
    async def get_video_result(self, task_id: str) -> Dict[str, any]:
        """
        查询GLM视频生成结果（与图片查询相同的接口）
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务状态和结果
        
        Raises:
            Exception: API调用失败
        """
        # 视频查询使用与图片相同的异步结果查询接口
        return await self.get_image_result(task_id)

