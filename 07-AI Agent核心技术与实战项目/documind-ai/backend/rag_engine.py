"""
RAG (Retrieval-Augmented Generation) 引擎
DocuMind AI 的核心组件 - 检索增强生成
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class RAGEngine:
    """
    RAG检索增强生成引擎
    
    功能：
    1. 文档解析和分块
    2. 向量化存储（使用ChromaDB）
    3. 语义检索
    4. 结合LLM生成回答
    """
    
    def __init__(self):
        """初始化RAG引擎"""
        if not CHROMA_AVAILABLE:
            raise ImportError("请安装chromadb: pip install chromadb")
        
        from app.config import settings
        
        self.settings = settings
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合（collection）
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"description": "DocuMind AI 文档向量库"}
        )
        
        # 文档元数据存储
        self.documents_meta: Dict[str, Dict] = {}
        
        print(f"✅ RAG引擎初始化完成 (文档数: {self.count_documents()})")
    
    def process_document(self, file_path: str, filename: str) -> str:
        """
        处理上传的文档
        
        流程：
        1. 解析文件内容
        2. 文本分块
        3. 生成向量嵌入并存储
        
        Args:
            file_path: 文件路径
            filename: 原始文件名
            
        Returns:
            document_id: 文档唯一标识符
        """
        # 生成文档ID
        doc_id = str(uuid.uuid4())[:8]
        
        # 解析文档内容
        text_content = self._parse_file(file_path)
        
        if not text_content or len(text_content.strip()) < 10:
            raise ValueError("文档内容为空或过短，无法处理")
        
        # 文本分块
        chunks = self._chunk_text(text_content)
        
        if not chunks:
            raise ValueError("文本分块失败")
        
        # 准备向量化数据
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            
            ids.append(chunk_id)
            documents.append(chunk['text'])
            metadatas.append({
                'doc_id': doc_id,
                'filename': filename,
                'chunk_index': i,
                'char_count': len(chunk['text']),
                'created_at': datetime.utcnow().isoformat()
            })
        
        # 批量添加到向量库
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        # 存储文档元数据
        self.documents_meta[doc_id] = {
            'id': doc_id,
            'filename': filename,
            'file_path': file_path,
            'total_chunks': len(chunks),
            'total_chars': len(text_content),
            'uploaded_at': datetime.utcnow().isoformat(),
            'status': 'processed'
        }
        
        print(f"📄 文档处理完成: {filename} ({len(chunks)}个文本块)")
        
        return doc_id
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        doc_ids: Optional[List[str]] = None,
        min_similarity: float = None
    ) -> List[Dict[str, Any]]:
        """
        语义检索相关文档片段
        
        Args:
            query: 查询问题
            top_k: 返回最相关的K个结果
            doc_ids: 限定在指定文档范围内查询
            min_similarity: 最小相似度阈值
            
        Returns:
            相关文档片段列表（按相似度排序）
        """
        top_k = top_k or self.settings.TOP_K_RETRIEVAL
        min_similarity = min_similarity or self.settings.SIMILARITY_THRESHOLD
        
        # 构建过滤条件
        where_filter = None
        if doc_ids:
            where_filter = {"doc_id": {"$in": doc_ids}}
        
        # 执行向量检索
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=['documents', 'metadatas', 'distances']
        )
        
        # 处理结果
        retrieved_chunks = []
        
        if results and results['ids'] and results['ids'][0]:
            for i, chunk_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                similarity = 1 - distance  # ChromaDB返回的是距离，需要转换
                
                # 过滤低相似度结果
                if similarity >= min_similarity:
                    retrieved_chunks.append({
                        'id': chunk_id,
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': round(similarity, 4),
                        'distance': round(distance, 4)
                    })
        
        return retrieved_chunks
    
    def generate_context_for_llm(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        max_chars: int = 4000
    ) -> str:
        """
        为LLM生成上下文提示
        
        将检索到的文档片段格式化为适合LLM理解的上下文
        """
        context_parts = ["以下是参考文档的相关内容：\n"]
        
        total_chars = 0
        for i, chunk in enumerate(retrieved_chunks[:5]):  # 最多使用前5个片段
            source_info = f"[来源: {chunk['metadata']['filename']} | 相似度: {chunk['similarity']:.2f}]"
            content = chunk['content']
            
            entry = f"\n--- 参考资料 {i+1} ---\n{source_info}\n{content}\n"
            
            if total_chars + len(entry) > max_chars:
                context_parts.append("\n... [因长度限制，部分参考资料已省略] ...")
                break
            
            context_parts.append(entry)
            total_chars += len(entry)
        
        return "".join(context_parts)
    
    def list_documents(self) -> List[Dict]:
        """获取所有已处理的文档列表"""
        return list(self.documents_meta.values())
    
    def delete_document(self, doc_id: str) -> bool:
        """删除指定文档及其所有向量数据"""
        if doc_id not in self.documents_meta:
            return False
        
        # 删除向量数据
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(f"删除向量数据失败: {e}")
        
        # 删除元数据
        del self.documents_meta[doc_id]
        
        return True
    
    def count_documents(self) -> int:
        """统计已处理的文档数量"""
        return self.collection.count()
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            self.collection.peek(limit=1)
            return True
        except Exception as e:
            print(f"RAG引擎健康检查失败: {e}")
            return False
    
    # ===== 私有方法 =====
    
    def _parse_file(self, file_path: str) -> str:
        """解析不同格式的文件"""
        ext = file_path.split('.')[-1].lower()
        
        if ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == 'md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == 'pdf':
            return self._parse_pdf(file_path)
        
        elif ext == 'docx':
            return self._parse_docx(file_path)
        
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    def _parse_pdf(self, file_path: str) -> str:
        """解析PDF文件（简化版）"""
        try:
            import PyPDF2
            
            text_parts = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            return "\n\n".join(text_parts)
            
        except ImportError:
            raise ImportError("PDF解析需要安装PyPDF2: pip install PyPDF2")
    
    def _parse_docx(self, file_path: str) -> str:
        """解析Word文档（简化版）"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
            
            return "\n\n".join(text_parts)
            
        except ImportError:
            raise ImportError("DOCX解析需要安装python-docx: pip install python-docx")
    
    def _chunk_text(self, text: str) -> List[Dict]:
        """
        文本分块策略
        
        使用固定大小的滑动窗口进行分块，
        保持段落完整性优先
        """
        chunk_size = self.settings.CHUNK_SIZE
        overlap = self.settings.CHUNK_OVERLAP
        
        # 按段落分割
        paragraphs = text.split('\n')
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 1 <= chunk_size:
                current_chunk += paragraph + "\n"
            else:
                if current_chunk.strip():
                    chunks.append({
                        'text': current_chunk.strip(),
                        'length': len(current_chunk.strip())
                    })
                
                # 带重叠开始新块
                if overlap > 0 and current_chunk:
                    current_chunk = current_chunk[-overlap:] + paragraph + "\n"
                else:
                    current_chunk = paragraph + "\n"
        
        # 最后一个块
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'length': len(current_chunk.strip())
            })
        
        return chunks
