"""
写作者 Agent (Writer Agent)
负责内容生成、摘要撰写、报告编写等任务
"""

from typing import List, Dict, Any, Optional
import json


class WriterAgent:
    """
    写作者智能体
    
    核心能力：
    1. 文档摘要生成
    2. 分析报告撰写
    3. 内容改写与优化
    4. 多文档综合分析
    """
    
    def __init__(self, rag_engine):
        """
        初始化写作者Agent
        
        Args:
            rag_engine: RAG引擎实例
        """
        self.rag_engine = rag_engine
        self.llm_client = None
        
        # 初始化LLM客户端
        self._init_llm_client()
        
        # 系统提示词
        self.system_prompt = """你是一位专业的技术写作专家，擅长将复杂的信息转化为清晰、结构化的内容。

**写作原则：**
1. **逻辑清晰** - 使用层次化结构组织内容
2. **语言精炼** - 避免冗余，表达准确
3. **专业规范** - 使用标准术语和格式
4. **读者导向** - 考虑目标读者的理解能力

**输出要求：**
- 使用Markdown格式
- 合理使用标题、列表、表格等元素
- 重要概念加粗或高亮
- 保持客观中立的语气"""
    
    def _init_llm_client(self):
        """初始化LLM客户端"""
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            if api_key:
                from deepseek_client import DeepSeekClient
                self.llm_client = DeepSeekClient()
                print("✅ 写作者Agent LLM客户端就绪")
        except Exception as e:
            print(f"⚠️ 初始化LLM客户端失败: {e}")
    
    def summarize_document(self, doc_id: str) -> str:
        """
        生成文档摘要
        
        Args:
            doc_id: 文档ID
            
        Returns:
            生成的摘要文本
        """
        # 检索文档的所有片段
        chunks = self.rag_engine.retrieve(
            query="这个文档的主要内容是什么？请总结核心观点",
            doc_ids=[doc_id],
            top_k=10,
            min_similarity=0.3  # 降低阈值以获取更多上下文
        )
        
        if not chunks:
            return "无法生成摘要：文档内容为空或未找到相关内容"
        
        # 构建提示词
        context_parts = []
        for chunk in chunks:
            context_parts.append(chunk['content'])
        
        full_context = "\n\n".join(context_parts[:8])  # 使用前8个片段
        
        prompt = f"""请为以下文档生成一份结构化的摘要。

**原文内容：**
{full_context[:6000]}

**摘要要求：**
1. 📌 **一句话总结** - 用一句话概括文档的核心主题
2. 🔑 **关键要点** - 列出3-5个主要观点或信息点
3. 📋 **详细概述** - 分段详细介绍各部分内容（200-400字）
4. 💡 **价值与应用** - 说明该文档的价值和适用场景
5. ⚠️ **注意事项** - 如有重要限制或前提条件需注明

请用中文输出，使用Markdown格式。"""
        
        if self.llm_client:
            result = self.llm_client.chat(
                message=prompt,
                system_prompt=self.system_prompt,
                temperature=0.4,
                max_tokens=2048
            )
            
            if result["success"]:
                return result["content"]
        
        # 简化版摘要
        return self._generate_simple_summary(chunks)
    
    def generate_analysis_report(
        self,
        doc_ids: List[str],
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        生成多文档分析报告
        
        Args:
            doc_ids: 要分析的文档ID列表
            analysis_type: 分析类型
                - general: 综合分析
                - compare: 对比分析
                - extract: 信息提取
                
        Returns:
            包含完整报告的字典
        """
        start_time = __import__('time').time()
        
        # 收集所有文档的信息
        all_documents_info = []
        for doc_id in doc_ids:
            chunks = self.rag_engine.retrieve(
                query="文档的主要内容和关键信息",
                doc_ids=[doc_id],
                top_k=5
            )
            
            if chunks:
                all_documents_info.append({
                    'doc_id': doc_id,
                    'chunks': chunks,
                    'sample_content': "\n".join([c['content'] for c in chunks[:3]])
                })
        
        if not all_documents_info:
            return {
                "success": False,
                "error": "没有找到可分析的文档内容",
                "report": ""
            }
        
        # 根据分析类型生成不同的报告
        if analysis_type == "compare":
            report = self._generate_comparison_report(all_documents_info)
        elif analysis_type == "extract":
            report = self._generate_extraction_report(all_documents_info)
        else:
            report = self._generate_general_report(all_documents_info)
        
        elapsed_ms = round((__import__('time').time() - start_time) * 1000, 2)
        
        return {
            "success": True,
            "report": report,
            "documents_analyzed": len(doc_ids),
            "analysis_type": analysis_type,
            "generation_time_ms": elapsed_ms,
            "metadata": {
                "model": "writer-agent-v1",
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
        }
    
    def rewrite_content(
        self,
        original_text: str,
        style: str = "formal",
        target_length: Optional[int] = None
    ) -> str:
        """
        内容改写
        
        Args:
            original_text: 原始文本
            style: 目标风格（formal/casual/academic/business）
            target_length: 目标长度（字符数）
            
        Returns:
            改写后的文本
        """
        style_guide = {
            "formal": "正式、专业，适合商务报告或学术论文",
            "casual": "轻松、口语化，适合博客或社交媒体",
            "academic": "学术严谨，适合研究论文",
            "business": "简洁明了，适合商业提案"
        }
        
        prompt = f"""请将以下文本改写为{style}风格。

**风格要求：** {style_guide.get(style, style)}

**原文：**
{original_text}

{"**字数要求：** 约" + str(target_length) + "字" if target_length else ""}

请保持原意不变，仅调整语言风格和表达方式。"""
        
        if self.llm_client:
            result = self.llm_client.chat(
                message=prompt,
                system_prompt="你是一个专业的文字编辑，擅长不同风格的写作转换。",
                temperature=0.6,
                max_tokens=2048
            )
            
            if result["success"]:
                return result["content"]
        
        return original_text
    
    def _generate_general_report(self, docs_info: List[Dict]) -> str:
        """生成综合分析报告"""
        sections = [
            "# 📊 多文档综合分析报告\n",
            f"## 报告概览\n本报告对 {len(docs_info)} 个文档进行了综合分析。\n",
            "## 各文档概要\n"
        ]
        
        for i, doc_info in enumerate(docs_info, 1):
            sample = doc_info['sample_content'][:300]
            sections.append(f"### 文档 {i}: {doc_info['doc_id']}\n")
            sections.append(f"{sample}...\n")
        
        sections.append("\n## 综合发现\n")
        sections.append("*基于对上述文档的分析，以下是主要发现：*\n\n")
        sections.append("(需要配置DeepSeek API以获得完整的AI分析)\n")
        
        return "".join(sections)
    
    def _generate_comparison_report(self, docs_info: List[Dict]) -> str:
        """生成对比分析报告"""
        return f"""# 📈 文档对比分析报告

## 对比维度

| 维度 | 文档1 | 文档2 | 差异 |
|------|-------|-------|------|
| 长度 | {len(docs_info[0]['sample_content'])}字 | {len(docs_info[1]['sample_content']) if len(docs_info)>1 else 'N/A'}字 | - |
| 主题 | 待分析 | 待分析 | - |

## 详细对比

*(需要配置DeepSeek API以获得完整的AI对比分析)*
"""
    
    def _generate_extraction_report(self, docs_info: List[Dict]) -> str:
        """生成信息提取报告"""
        return f"""# 🔍 关键信息提取报告

## 提取结果

从 {len(docs_info)} 个文档中提取的关键信息如下：

### 关键实体
*(待提取)*

### 重要数据
*(待提取)*

### 核心观点
*(待提取)*

---
*注：配置DeepSeek AI后可自动提取以上信息*
"""
    
    def _generate_simple_summary(self, chunks: List[Dict]) -> str:
        """简化版摘要（无LLM时）"""
        total_chars = sum(len(c['content']) for c in chunks)
        
        summary_parts = [
            "## 📄 文档摘要\n",
            f"**文档长度**: {total_chars:,} 字符\n",
            f"**检索片段数**: {len(chunks)}\n\n",
            "### 主要内容预览\n"
        ]
        
        for i, chunk in enumerate(chunks[:3], 1):
            content_preview = chunk['content'][:250]
            summary_parts.append(f"**片段{i}:**\n{content_preview}...\n")
        
        summary_parts.append("\n---\n*⚠️ 当前为简化模式。配置DeepSeek API后可获得更详细的智能摘要。*")
        
        return "".join(summary_parts)


# ===== 使用示例 =====

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     ✍️ 写作者 Agent 演示                  ║
║     Day 7 AI Agent 核心技术               ║
╚══════════════════════════════════════╝
    """)
    
    print("⚠️ 此模块需要配合RAG引擎使用")
    print("   请通过 main.py 启动完整应用")
