"""
DeepSeek API客户端封装 - Day 6 AI基础应用
提供对话、代码生成、情感分析等功能
"""

import httpx
import json
import time
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass


@dataclass
class DeepSeekConfig:
    """DeepSeek配置"""
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: float = 30.0


class DeepSeekClient:
    """DeepSeek大模型API客户端"""
    
    def __init__(self, config: Optional[DeepSeekConfig] = None):
        """
        初始化DeepSeek客户端
        
        Args:
            config: 配置对象，如果为None则从环境变量加载
        """
        if config is None:
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            config = DeepSeekConfig(
                api_key=os.getenv("DEEPSEEK_API_KEY", "")
            )
        
        self.config = config
        self.client = httpx.Client(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=config.timeout
        )
        
        self.conversation_history: List[Dict[str, str]] = []
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        发送对话请求
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（0-2，越高越随机）
            max_tokens: 最大生成token数
            stream: 是否使用流式输出
            
        Returns:
            包含响应内容和元数据的字典
        """
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史消息
        messages.extend(self.conversation_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": stream
        }
        
        start_time = time.time()
        
        try:
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # 提取回复内容
            assistant_message = result["choices"][0]["message"]["content"]
            
            # 更新对话历史
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # 保持历史记录在合理范围内
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-10:]
            
            elapsed_time = time.time() - start_time
            
            return {
                "success": True,
                "content": assistant_message,
                "model": result.get("model"),
                "usage": result.get("usage", {}),
                "response_time_ms": round(elapsed_time * 1000, 2),
                "provider": "deepseek"
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP错误 {e.response.status_code}"
            try:
                error_detail = e.response.json().get("error", {}).get("message", "")
                if error_detail:
                    error_msg += f": {error_detail}"
            except:
                pass
            
            return {
                "success": False,
                "error": error_msg,
                "status_code": e.response.status_code
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_code(
        self,
        description: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        代码生成
        
        Args:
            description: 功能描述
            language: 编程语言（python, javascript, java等）
            context: 额外上下文或代码片段
            
        Returns:
            生成的代码和说明
        """
        system_prompt = f"""你是一个专业的{language}程序员。
请根据用户的描述生成高质量、可运行的{language}代码。

要求：
1. 代码要有清晰的注释
2. 遵循最佳实践和编码规范
3. 包含必要的错误处理
4. 如果需要，提供使用示例"""

        user_message = f"请用{language}实现以下功能：\n\n{description}"
        
        if context:
            user_message += f"\n\n参考上下文/已有代码：\n```\n{context}\n```"
        
        return self.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.3,  # 降低温度以获得更确定性的输出
            max_tokens=4096
        )
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        情感分析
        
        Args:
            text: 待分析的文本
            
        Returns:
            情感分类结果（积极/消极/中性）及置信度
        """
        system_prompt = """你是一个情感分析专家。请对给定的文本进行情感分析，并以JSON格式返回结果。

返回格式：
{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,
    "keywords": ["关键词1", "关键词2"],
    "summary": "简短总结"
}"""
        
        user_message = f"请分析以下文本的情感倾向：\n{text}"
        
        result = self.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=500
        )
        
        if result["success"]:
            try:
                content = result["content"]
                # 尝试提取JSON部分
                if "{" in content and "}" in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    analysis = json.loads(json_str)
                    result["analysis"] = analysis
            except:
                result["analysis"] = {"raw_response": result["content"]}
        
        return result
    
    def summarize_text(
        self,
        text: str,
        max_length: int = 200,
        style: str = "简洁"
    ) -> Dict[str, Any]:
        """
        文本摘要
        
        Args:
            text: 原始文本
            max_length: 摘要最大长度（字符数）
            style: 摘要风格（简洁/详细/要点）
            
        Returns:
            生成的摘要
        """
        system_prompt = f"""你是一个专业的文本摘要助手。请生成{style}风格的摘要。

要求：
1. 摘要长度控制在{max_length}字以内
2. 保留关键信息和主要观点
3. 语言通顺流畅
4. 如果是长文，可以分点列出要点"""
        
        user_message = f"请对以下文本进行摘要：\n\n{text[:4000]}"  # 截断过长文本
        
        return self.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=max_length * 2
        )
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        print("✅ 对话历史已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取会话统计信息"""
        return {
            "provider": "deepseek",
            "model": self.config.model,
            "conversation_turns": len(self.conversation_history) // 2,
            "history_messages_count": len(self.conversation_history)
        }
    
    def close(self):
        """关闭HTTP客户端"""
        self.client.close()


# ===== 使用示例 =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     🤖 DeepSeek API 客户端演示           ║
║     Day 6 AI基础理论与国内大模型应用      ║
╚════════════════════════════════════════╝
    """)
    
    client = DeepSeekClient()
    
    if not client.config.api_key:
        print("❌ 未配置API密钥！")
        print("   请设置环境变量 DEEPSEEK_API_KEY 或创建 .env 文件")
        print("\n   示例 .env 文件内容:")
        print("   DEEPSEEK_API_KEY=your-api-key-here")
    else:
        print(f"✅ DeepSeek客户端初始化成功 (模型: {client.config.model})\n")
        
        # 测试1: 简单对话
        print("="*60)
        print("📝 测试1: 简单对话")
        print("="*60)
        
        result = client.chat("你好，请简单介绍一下你自己")
        
        if result["success"]:
            print(f"✅ 回复: {result['content'][:200]}...")
            print(f"⏱️ 响应时间: {result['response_time_ms']}ms")
            print(f"📊 Token使用: {result['usage']}")
        else:
            print(f"❌ 错误: {result.get('error')}")
        
        print()
        
        # 测试2: 代码生成
        print("="*60)
        print("💻 测试2: 代码生成")
        print("="*60)
        
        code_result = client.generate_code(
            description="实现一个快速排序算法",
            language="python"
        )
        
        if code_result["success"]:
            print(f"✅ 生成的代码:\n{code_result['content'][:500]}...")
        else:
            print(f"❌ 错误: {code_result.get('error')}")
        
        print()
        
        # 显示统计信息
        stats = client.get_stats()
        print("="*60)
        print("📊 会话统计")
        print("="*60)
        for k, v in stats.items():
            print(f"{k}: {v}")
    
    client.close()
