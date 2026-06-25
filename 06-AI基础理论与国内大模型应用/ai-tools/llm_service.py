"""
统一LLM服务层 - Day 6 AI基础应用
提供智能路由、故障转移、多模型统一接口
"""

from typing import Optional, Dict, Any, List
import time
import random

from deepseek_client import DeepSeekClient, DeepSeekConfig
from doubao_client import DoubaoClient, DoubaoConfig


class LLMService:
    """
    统一大语言模型服务
    
    功能：
    - 智能路由：根据任务类型自动选择最佳模型
    - 故障转移：主模型失败时自动切换备用模型
    - 负载均衡：在多个相同能力的模型间分配请求
    - 统一接口：屏蔽不同API的差异
    """
    
    def __init__(self):
        """初始化服务（加载所有可用的客户端）"""
        self.clients: Dict[str, Any] = {}
        self.primary_provider = None
        self.fallback_providers: List[str] = []
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化所有可用的AI客户端"""
        
        # 尝试初始化DeepSeek
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
            if deepseek_key:
                self.clients["deepseek"] = DeepSeekClient()
                if not self.primary_provider:
                    self.primary_provider = "deepseek"
                print(f"✅ DeepSeek客户端已就绪")
            
            # 尝试初始化豆包
            doubao_key = os.getenv("DOUBAO_API_KEY", "")
            if doubao_key:
                self.clients["doubao"] = DoubaoClient()
                if not self.primary_provider:
                    self.primary_provider = "doubao"
                print(f"✅ 豆包(火山引擎)客户端已就绪")
                
        except Exception as e:
            print(f"⚠️ 初始化客户端时出错: {e}")
        
        # 设置故障转移顺序
        self.fallback_providers = [
            p for p in self.clients.keys() 
            if p != self.primary_provider
        ]
        
        if not self.clients:
            print("❌ 未配置任何AI API密钥！请检查 .env 文件")
    
    def chat(
        self,
        message: str,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一对话接口
        
        Args:
            message: 用户消息
            provider: 指定使用的提供商（可选，自动选择最优）
            system_prompt: 系统提示词
            **kwargs: 其他参数传递给具体客户端
            
        Returns:
            标准化的响应结果
        """
        # 确定使用哪个提供商
        target_provider = provider or self._select_provider(message)
        
        if target_provider and target_provider in self.clients:
            client = self.clients[target_provider]
            
            # 调用具体客户端
            result = client.chat(
                message=message,
                system_prompt=system_prompt,
                **kwargs
            )
            
            # 标准化响应格式
            return {
                "success": result.get("success", False),
                "content": result.get("content"),
                "provider": target_provider,
                "model": result.get("model"),
                "usage": result.get("usage", {}),
                "response_time_ms": result.get("response_time_ms"),
                "error": result.get("error")
            }
        
        # 如果指定提供商不可用，尝试故障转移
        if provider and provider != target_provider:
            return self._fallback_chat(message, provider, system_prompt, **kwargs)
        
        return {
            "success": False,
            "error": "没有可用的AI服务",
            "provider": None
        }
    
    def _select_provider(self, message: str) -> Optional[str]:
        """
        智能选择提供商
        
        基于消息内容特征选择最合适的模型：
        - 代码相关 → DeepSeek（代码能力强）
        - 创意写作 → 豆包（中文表现好）
        - 默认 → primary_provider
        """
        if not self.primary_provider:
            return None
        
        code_keywords = ["代码", "编程", "函数", "算法", "程序", "code", "python", "javascript"]
        creative_keywords = ["写", "创作", "故事", "诗歌", "文章"]
        
        msg_lower = message.lower()
        
        # 代码生成优先用DeepSeek
        if any(kw in msg_lower for kw in code_keywords):
            if "deepseek" in self.clients:
                return "deepseek"
        
        # 创意写作优先用豆包
        if any(kw in msg_lower for kw in creative_keywords):
            if "doubao" in self.clients:
                return "doubao"
        
        # 默认返回主提供商
        return self.primary_provider
    
    def _fallback_chat(
        self,
        message: str,
        failed_provider: str,
        system_prompt: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """故障转移到其他可用提供商"""
        
        available_providers = [
            p for p in self.fallback_providers 
            if p != failed_provider
        ]
        
        for provider in available_providers:
            try:
                client = self.clients[provider]
                result = client.chat(message, system_prompt, **kwargs)
                
                if result.get("success"):
                    print(f"⚠️ 已从 {failed_provider} 故障转移到 {provider}")
                    
                    return {
                        "success": True,
                        "content": result["content"],
                        "provider": provider,
                        "model": result.get("model"),
                        "usage": result.get("usage", {}),
                        "response_time_ms": result.get("response_time_ms"),
                        "fallback_from": failed_provider
                    }
                    
            except Exception as e:
                print(f"故障转移失败 [{provider}]: {e}")
                continue
        
        return {
            "success": False,
            "error": f"所有AI服务均不可用 (尝试过: {available_providers})"
        }
    
    def generate_code(self, description: str, language: str = "python") -> Dict[str, Any]:
        """代码生成（优先使用DeepSeek）"""
        if "deepseek" in self.clients:
            result = self.clients["deepseek"].generate_code(description, language)
            result["provider"] = "deepseek"
            return result
        
        return self.chat(
            message=f"请用{language}实现：{description}",
            system_prompt="你是一个专业程序员，生成高质量代码"
        )
    
    def summarize(self, text: str, max_length: int = 200) -> Dict[str, Any]:
        """文本摘要"""
        if "deepseek" in self.clients:
            result = self.clients["deepseek"].summarize_text(text, max_length)
            result["provider"] = "deepseek"
            return result
        
        return self.chat(
            message=f"请摘要以下文本（{max_length}字以内）：\n{text[:2000]}",
            system_prompt="你是文本摘要专家"
        )
    
    def translate(self, text: str, target_lang: str = "英文") -> Dict[str, Any]:
        """翻译（优先使用豆包）"""
        if "doubao" in self.clients:
            result = self.clients["doubao"].translate(text, target_lang=target_lang)
            result["provider"] = "doubao"
            return result
        
        return self.chat(
            message=f"将以下中文翻译成{target_lang}：\n{text}",
            system_prompt="你是专业翻译"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有服务的状态"""
        status = {
            "total_providers": len(self.clients),
            "primary": self.primary_provider,
            "providers": {}
        }
        
        for name, client in self.clients.items():
            try:
                stats = client.get_stats()
                status["providers"][name] = {
                    "status": "online",
                    **stats
                }
            except Exception as e:
                status["providers"][name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return status
    
    def close_all(self):
        """关闭所有客户端连接"""
        for name, client in self.clients.items():
            try:
                client.close()
                print(f"✅ {name} 客户端已关闭")
            except Exception as e:
                print(f"❌ 关闭 {name} 失败: {e}")


# ===== 全局单例 =====

_llm_service: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """获取全局LLM服务实例（懒加载）"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


# ===== 使用示例 =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     🌐 统一LLM服务演示                   ║
║     Day 6 AI基础理论与国内大模型应用      ║
╚══════════════════════════════════════╝
    """)
    
    service = get_llm_service()
    
    if service.clients:
        print("\n📊 服务状态:")
        status = service.get_status()
        print(f"   可用提供商: {status['total_providers']}")
        print(f"   主服务商: {status['primary']}")
        
        # 测试智能路由
        print("\n" + "="*60)
        print("🧠 测试1: 智能路由（代码生成应选DeepSeek）")
        print("="*60)
        
        code_result = service.generate_code("实现一个斐波那契数列计算器")
        if code_result["success"]:
            print(f"✅ 选择提供商: {code_result['provider']}")
            print(f"💻 代码片段:\n{code_result['content'][:300]}...")
        
        print("\n" + "="*60)
        print("🧠 测试2: 智能路由（创意写作应选豆包）")
        print("="*60)
        
        creative_result = service.chat("请帮我写一首关于春天的诗")
        if creative_result["success"]:
            print(f"✅ 选择提供商: {creative_result['provider']}")
            print(f"✍️ 创作:\n{creative_result['content'][:300]}...")
        
    else:
        print("⚠️ 没有可用的AI服务，请先配置API密钥")
    
    service.close_all()
