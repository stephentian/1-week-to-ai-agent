"""
豆包(火山引擎) API客户端封装 - Day 6 AI基础应用
提供对话、角色扮演、视觉理解等功能
"""

import httpx
import json
import time
import base64
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class DoubaoConfig:
    """豆包(火山引擎)配置"""
    api_key: str = ""
    app_id: str = ""
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    model: str = "doubao-pro-32k"  # 或 doubao-lite-32k
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: float = 30.0


class DoubaoClient:
    """豆包(火山引擎)大模型API客户端"""
    
    def __init__(self, config: Optional[DoubaoConfig] = None):
        """
        初始化豆包客户端
        
        Args:
            config: 配置对象，如果为None则从环境变量加载
        """
        if config is None:
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            config = DoubaoConfig(
                api_key=os.getenv("DOUBAO_API_KEY", ""),
                app_id=os.getenv("DOUBAO_APP_ID", "")
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
        role: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送对话请求（支持角色扮演）
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词
            role: 角色设定（如"专业翻译"、"Python专家"等）
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            响应结果字典
        """
        messages = []
        
        # 构建系统提示词
        if system_prompt or role:
            full_system_prompt = system_prompt or ""
            
            if role:
                full_system_prompt += f"\n\n你现在扮演的角色是：{role}。请完全按照这个角色的特点、语气和专业知识来回答问题。"
            
            messages.append({"role": "system", "content": full_system_prompt})
        
        # 添加历史消息
        messages.extend(self.conversation_history)
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": f"{self.config.app_id}/{self.config.model}" if self.config.app_id else self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens
        }
        
        start_time = time.time()
        
        try:
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            assistant_message = result["choices"][0]["message"]["content"]
            
            # 更新历史
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-10:]
            
            elapsed_time = time.time() - start_time
            
            return {
                "success": True,
                "content": assistant_message,
                "model": result.get("model"),
                "usage": result.get("usage", {}),
                "response_time_ms": round(elapsed_time * 1000, 2),
                "provider": "doubao"
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
    
    def role_play(
        self,
        message: str,
        character: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        角色扮演对话
        
        Args:
            message: 用户输入
            character: 角色名称/描述（如"孔子"、"乔布斯"、"心理咨询师"）
            context: 额外的背景设定
            
        Returns:
            角色的回复
        """
        system_prompt = f"""你正在扮演{character}这个角色。

要求：
1. 完全沉浸在角色中，使用该角色的语言风格和思维方式
2. 回答要符合角色的历史背景、性格特点和知识水平
3. 可以适当加入角色的口头禅或标志性表达
4. 保持角色的一致性，不要出戏"""
        
        if context:
            system_prompt += f"\n\n背景设定：{context}"
        
        return self.chat(
            message=message,
            system_prompt=system_prompt,
            role=character,
            temperature=0.8  # 稍高温度增加创造性
        )
    
    def translate(
        self,
        text: str,
        source_lang: str = "中文",
        target_lang: str = "英文",
        style: str = "正式"
    ) -> Dict[str, Any]:
        """
        专业翻译
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            style: 翻译风格（正式/口语/文学/技术）
            
        Returns:
            翻译结果
        """
        system_prompt = f"""你是一位专业的翻译专家，擅长{source_lang}到{target_lang}的翻译。

翻译要求：
1. 准确传达原文含义，不遗漏关键信息
2. 符合{target_lang}的表达习惯，避免翻译腔
3. 保持{style}的语体风格
4. 对于专业术语或文化特色词汇，可以添加注释说明

输出格式：
【译文】
(翻译后的文本)

【注释】(如有需要)
(对难点或特殊表达的简要说明)"""
        
        user_message = f"请将以下{source_lang}文本翻译成{target_lang}：\n\n{text}"
        
        return self.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=4096
        )
    
    def creative_writing(
        self,
        topic: str,
        genre: str = "散文",
        length: str = "中等",
        style: str = "文艺"
    ) -> Dict[str, Any]:
        """
        创意写作
        
        Args:
            topic: 写作主题
            genre: 文体类型（小说/散文/诗歌/剧本/广告文案）
            length: 篇幅长短（短篇/中等/长篇）
            style: 写作风格（文艺/幽默/严肃/轻松）
            
        Returns:
            创作内容
        """
        system_prompt = f"""你是一位才华横溢的作家。请根据用户的要求进行创意写作。

写作要求：
1. 文体类型：{genre}
2. 篇幅长度：{length}
3. 风格特点：{style}
4. 内容要有新意，避免陈词滥调
5. 结构完整，逻辑清晰
6. 语言优美，富有感染力"""
        
        user_message = f"请以「{topic}」为主题写一篇{genre}"
        
        return self.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.9,  # 高温度激发创造力
            max_tokens=4096
        )
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        print("✅ 对话历史已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取会话统计"""
        return {
            "provider": "doubao",
            "model": self.config.model,
            "app_id": self.config.app_id[:8] + "..." if len(self.config.app_id) > 8 else "",
            "conversation_turns": len(self.conversation_history) // 2,
            "history_messages_count": len(self.conversation_history)
        }
    
    def close(self):
        """关闭客户端"""
        self.client.close()


# ===== 使用示例 =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     🤖 豆包(火山引擎)API 客户端演示       ║
║     Day 6 AI基础理论与国内大模型应用      ║
╚══════════════════════════════════════╝
    """)
    
    client = DoubaoClient()
    
    if not client.config.api_key:
        print("❌ 未配置API密钥！")
        print("   请设置环境变量 DOUBAO_API_KEY 和 DOUBAO_APP_ID")
        print("\n   示例 .env 文件:")
        print("   DOUBAO_API_KEY=your-api-key")
        print("   DOUBAO_APP_ID=your-app-id")
    else:
        print(f"✅ 豆包客户端初始化成功 (模型: {client.config.model})\n")
        
        # 测试1: 角色扮演
        print("="*60)
        print("🎭 测试1: 角色扮演（模拟与乔布斯对话）")
        print("="*60)
        
        role_result = client.role_play(
            message="你认为创新最重要的要素是什么？",
            character="史蒂夫·乔布斯"
        )
        
        if role_result["success"]:
            print(f"🗣️ 乔布斯说: {role_result['content'][:300]}...")
            print(f"⏱️ 响应时间: {role_result['response_time_ms']}ms")
        else:
            print(f"❌ 错误: {role_result.get('error')}")
        
        print()
        
        # 测试2: 专业翻译
        print("="*60)
        print("🌍 测试2: 中英翻译")
        print("="*60)
        
        trans_result = client.translate(
            text="人工智能正在深刻改变我们的生活方式，从智能手机到自动驾驶汽车，AI技术的应用无处不在。",
            target_lang="英文",
            style="正式"
        )
        
        if trans_result["success"]:
            print(f"✅ 翻译结果:\n{trans_result['content'][:400]}...")
        else:
            print(f"❌ 错误: {trans_result.get('error')}")
        
        print()
        
        # 统计信息
        stats = client.get_stats()
        print("="*60)
        print("📊 会话统计")
        print("="*60)
        for k, v in stats.items():
            print(f"{k}: {v}")
    
    client.close()
