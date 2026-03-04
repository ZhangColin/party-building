"""会话标题生成服务"""
import logging
from typing import Optional, Tuple
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class TitleGenerator:
    """会话标题生成器"""
    
    def __init__(self):
        """初始化标题生成器"""
        self.client, self.model_name = self._get_ai_client()
    
    def _get_ai_client(self) -> Tuple[Optional[OpenAI], str]:
        """
        获取 AI 客户端和模型名称
        优先级：TITLE_GENERATION_MODEL > DeepSeek > CURRENT_PROVIDER
        
        Returns:
            (client, model_name) 元组
        """
        # 1. 检查是否配置了标题生成专用模型
        title_model_config = os.getenv("TITLE_GENERATION_MODEL")
        if title_model_config and ":" in title_model_config:
            provider, model_name = title_model_config.split(":", 1)
            provider = provider.lower()
            logger.info(f"标题生成使用配置的专用模型: {provider}:{model_name}")
        else:
            # 2. 优先尝试 DeepSeek（成本最低）
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if api_key and api_key.startswith("sk-"):
                provider = "deepseek"
                model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
                logger.info(f"标题生成使用 DeepSeek（成本优先）")
            else:
                # 3. 使用当前配置的服务商
                provider = os.getenv("CURRENT_PROVIDER", "deepseek").lower()
                model_name = None  # 稍后从环境变量读取
                logger.info(f"标题生成使用系统默认服务商: {provider}")
        
        # 根据服务商获取配置
        api_key = ""
        base_url = ""
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            if not model_name:
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
        else:
            logger.warning(f"标题生成服务：未知的服务商 [{provider}]")
            return None, ""
        
        # 校验 API Key
        if not api_key or not api_key.startswith("sk-"):
            logger.warning("标题生成服务：未找到有效的 API Key")
            return None, ""
        
        # 创建客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,  # 标题生成使用较短的超时时间
            max_retries=1  # 只重试一次
        )
        
        logger.info(f"标题生成服务初始化成功 - 服务商: {provider}, 模型: {model_name}")
        return client, model_name
    
    async def generate_title(
        self,
        user_message: str,
        ai_response: Optional[str] = None
    ) -> str:
        """
        智能生成会话标题

        策略：
        1. 用户消息为空：直接返回"新对话"
        2. 如果用户消息 < 10字符：使用用户消息+AI回复前300字
        3. 否则：只使用用户消息前500字

        Args:
            user_message: 用户消息
            ai_response: AI回复（可选）

        Returns:
            生成的标题（8-15个字）
        """
        user_msg = user_message.strip()

        # 如果用户消息为空，直接返回默认标题
        if not user_msg:
            return "新对话"

        # 如果没有AI客户端，使用降级方案
        if not self.client:
            return self._fallback_title(user_message)

        # 策略选择：短消息需要AI回复辅助
        if len(user_msg) < 10:
            ai_preview = (ai_response[:300] if ai_response else "")
            prompt = f"""请为以下对话生成一个简洁的标题（8-15个字）。
用户消息：{user_msg}
AI回复：{ai_preview}

直接输出标题，无需标点："""
        else:
            # 长消息只用用户消息（限制500字符以控制成本）
            prompt = f"""请为以下用户提问生成一个简洁的标题（8-15个字）。
用户提问：{user_msg[:500]}

直接输出标题，无需标点："""

        try:
            logger.info(f"开始生成会话标题 - 用户消息长度: {len(user_msg)}, 使用模型: {self.model_name}")

            response = self.client.chat.completions.create(
                model=self.model_name,  # 使用配置的模型
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30,  # 标题不需要太长
                temperature=0.7
            )

            title = response.choices[0].message.content.strip()

            # 清理标题（去除标点符号）
            title = self._clean_title(title)

            # 限制长度
            if len(title) > 30:
                title = title[:30]

            logger.info(f"标题生成成功: {title}")
            return title if title else "新对话"

        except Exception as e:
            logger.error(f"AI生成标题失败: {e}")
            # 降级方案
            return self._fallback_title(user_message)

    def _clean_title(self, title: str) -> str:
        """
        清理标题，移除标点符号

        Args:
            title: 原始标题

        Returns:
            清理后的标题
        """
        # 定义需要移除的标点符号
        punctuation = '"\'。，！？、：；""''《》【】（）[]{}、，。！？；：'

        # 移除所有标点符号
        for char in punctuation:
            title = title.replace(char, '')

        return title.strip()
    
    def _fallback_title(self, user_message: str) -> str:
        """
        降级方案：使用简单截取生成标题

        Args:
            user_message: 用户消息

        Returns:
            截取的标题（最多30个字符）
        """
        msg = user_message.strip()

        if not msg:
            return "新对话"

        # 去除换行符
        msg = msg.replace('\n', ' ').replace('\r', ' ')

        # 截取前30个字符，超过则添加"..."
        if len(msg) > 30:
            return msg[:30]
        else:
            return msg
