"""
研究员 Agent (Researcher Agent)
负责信息检索、文档查询、事实核查等任务
"""

from typing import List, Dict, Any, Optional
import json

try:
    from deepseek_client import DeepSeekClient
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False


class ResearcherAgent:
    """
    研究员智能体
    
    核心能力：
    1. 基于RAG的精准信息检索
    2. 多源信息综合分析
    3. 上下文理解与推理
    4. 引用来源追踪
    """
    
    def __init__(self, rag_engine):
        """
        初始化研究员Agent
        
        Args:
            rag_engine: RAG引擎实例（用于向量检索）
        """
        self.rag_engine = rag_engine
        self.llm_client = None
        
        # 初始化LLM客户端
        self._init_llm_client()
        
        # 系统提示词
        self.system_prompt = """你是一个专业的文档研究助手，基于提供的参考资料回答用户问题。

**核心原则：**
1. **准确性优先** - 只依据提供的参考资料回答，不要编造信息
2. **引用来源** - 明确标注信息来源（文件名、相关度）
3. **结构清晰** - 使用分点、列表等方式组织答案
4. **承认局限** - 如果资料中没有相关信息，明确说明

**回答格式：**
📌 **核心答案**
（直接回答用户的问题）

📚 **参考来源**
- 来源1 (相似度: XX%): 关键引用内容
- 来源2 (相似度: XX%): 补充说明

💡 **补充说明**（如有）
（额外的背景信息或注意事项）"""
    
    def _init_llm_client(self):
        """初始化LLM客户端"""
        try:
            if DEEPSEEK_AVAILABLE:
                from dotenv import load_dotenv
                import os
                load_dotenv()
                
                api_key = os.getenv("DEEPSEEK_API_KEY", "")
                if api_key:
                    self.llm_client = DeepSeekClient()
                    print("✅ 研究员Agent LLM客户端就绪")
        except Exception as e:
            print(f"⚠️ 初始化LLM客户端失败: {e}")
    
    def query(
        self,
        question: str,
        doc_ids: Optional[List[str]] = None,
        history: Optional[List[Dict]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        执行查询任务
        
        完整流程：检索 → 构建提示 → LLM生成 → 格式化输出
        
        Args:
            question: 用户问题
            doc_ids: 指定查询的文档ID列表（可选）
            history: 对话历史（可选，用于多轮对话）
            top_k: 检索的相关片段数量
            
        Returns:
            包含答案、引用来源、元数据的字典
        """
        start_time = __import__('time').time()
        
        # Step 1: 向量检索
        print(f"🔍 正在检索: {question[:50]}...")
        retrieved_chunks = self.rag_engine.retrieve(
            query=question,
            top_k=top_k,
            doc_ids=doc_ids
        )
        
        if not retrieved_chunks:
            return {
                "success": True,
                "answer": "抱歉，在现有文档中没有找到与您问题相关的信息。请尝试上传更多相关文档或调整问题的表述方式。",
                "sources": [],
                "retrieved_count": 0,
                "has_context": False,
                "response_time_ms": round((__import__('time').time() - start_time) * 1000, 2)
            }
        
        print(f"✅ 检索到 {len(retrieved_chunks)} 个相关片段")
        
        # Step 2: 构建LLM提示词
        context = self.rag_engine.generate_context_for_llm(question, retrieved_chunks)
        
        user_message = f"{context}\n\n**用户问题：**\n{question}"
        
        # 添加对话历史（如果有）
        if history and len(history) > 0:
            history_text = "\n".join([
                f"{'用户' if msg.get('role') == 'user' else '助手'}: {msg['content']}"
                for msg in history[-5:]  # 最近5轮对话
            ])
            user_message = f"**之前的对话记录：**\n{history_text}\n\n{user_message}"
        
        # Step 3: 调用LLM生成回答
        if not self.llm_client:
            # 如果没有LLM客户端，使用简单的模板回复
            answer = self._generate_simple_answer(question, retrieved_chunks)
        else:
            result = self.llm_client.chat(
                message=user_message,
                system_prompt=self.system_prompt,
                temperature=0.5,  # 较低温度确保准确性
                max_tokens=2048
            )
            
            if result["success"]:
                answer = result["content"]
            else:
                answer = f"AI服务暂时不可用。以下是检索到的相关内容摘要：\n\n" + \
                       "\n".join([f"- {c['content'][:200]}..." for c in retrieved_chunks[:3]])
        
        # Step 4: 格式化引用来源
        sources = []
        for chunk in retrieved_chunks[:3]:  # 最多显示前3个来源
            sources.append({
                "filename": chunk['metadata']['filename'],
                "similarity": chunk['similarity'],
                "snippet": chunk['content'][:150] + "..." if len(chunk['content']) > 150 else chunk['content']
            })
        
        elapsed_ms = round((__import__('time').time() - start_time) * 1000, 2)
        
        return {
            "success": True,
            "answer": answer,
            "sources": sources,
            "retrieved_count": len(retrieved_chunks),
            "has_context": True,
            "response_time_ms": elapsed_ms,
            "model": "researcher-agent-v1"
        }
    
    def stream_query(self, question: str):
        """
        流式查询（用于Server-Sent Events）
        
        逐块返回生成的文本，提升用户体验
        """
        # 先返回检索结果
        yield {"type": "retrieval_start", "message": "正在检索相关文档..."}
        
        chunks = self.rag_engine.retrieve(query=question, top_k=5)
        
        yield {
            "type": "retrieval_complete",
            "count": len(chunks),
            "message": f"找到 {len(chunks)} 个相关片段"
        }
        
        if not chunks:
            yield {
                "type": "complete",
                "content": "未找到相关文档内容"
            }
            return
        
        # 构建上下文并调用LLM流式输出
        context = self.rag_engine.generate_context_for_llm(question, chunks)
        
        if self.llm_client:
            yield {"type": "generation_start", "message": "正在生成回答..."}
            
            # 这里应该实现真正的流式输出
            # 简化版本：直接返回完整结果
            result = self.query(question)
            
            yield {
                "type": "chunk",
                "content": result["answer"]
            }
        
        yield {"type": "complete", "message": "回答完成"}
    
    def _generate_simple_answer(self, question: str, chunks: List[Dict]) -> str:
        """当LLM不可用时，生成简单答案"""
        answer_parts = [
            f"根据文档检索结果，关于「{question}」的相关信息如下：\n"
        ]
        
        for i, chunk in enumerate(chunks[:3], 1):
            source_info = f"来源: {chunk['metadata']['filename']} (相似度: {chunk['similarity']:.1%})"
            content = chunk['content'][:300]
            
            answer_parts.append(f"\n**{i}. {source_info}**\n{content}")
        
        answer_parts.append("\n\n*注：当前为简化模式，建议配置DeepSeek API以获得更准确的智能回答*")
        
        return "".join(answer_parts)
    
    def fact_check(self, statement: str) -> Dict[str, Any]:
        """
        事实核查
        
        验证某个陈述是否在文档中有支持证据
        """
        chunks = self.rag_engine.retrieve(
            query=statement,
            top_k=3,
            min_similarity=0.6
        )
        
        if not chunks:
            return {
                "statement": statement,
                "verdict": "not_found",
                "confidence": 0.0,
                "evidence": [],
                "summary": "在文档中未找到相关信息来验证该陈述"
            }
        
        best_match = max(chunks, key=lambda x: x['similarity'])
        
        if best_match['similarity'] >= 0.85:
            verdict = "supported"
        elif best_match['similarity'] >= 0.7:
            verdict = "partially_supported"
        else:
            verdict = "contradicted"
        
        return {
            "statement": statement,
            "verdict": verdict,
            "confidence": best_match['similarity'],
            "evidence": [
                {
                    "source": c['metadata']['filename'],
                    "snippet": c['content'][:200],
                    "similarity": c['similarity']
                } for c in chunks
            ],
            "summary": f"该陈述在文档中的验证结果：{verdict}"
        }


# ===== 使用示例 =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     🔬 研究员 Agent 演示                  ║
║     Day 7 AI Agent 核心技术               ║
╚══════════════════════════════════════╝
    """)
    
    # 注意：需要先初始化RAG引擎
    print("⚠️ 此模块需要配合RAG引擎使用")
    print("   请通过 main.py 启动完整应用")
