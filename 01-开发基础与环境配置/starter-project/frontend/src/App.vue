<template>
  <div id="app">
    <header class="header">
      <h1>🚀 AI Agent Starter</h1>
      <p class="subtitle">开发环境模板 - Day 1 实战项目</p>
    </header>

    <main class="main-content">
      <section class="card">
        <h2>✅ 环境检查</h2>
        <div class="status-list">
          <div class="status-item">
            <span class="label">前端框架:</span>
            <span class="value success">Vue 3 ✅</span>
          </div>
          <div class="status-item">
            <span class="label">构建工具:</span>
            <span class="value success">Vite ✅</span>
          </div>
          <div class="status-item">
            <span class="label">后端 API:</span>
            <span :class="['value', apiStatus ? 'success' : 'loading']">
              {{ apiStatus ? 'FastAPI ✅' : '检测中...' }}
            </span>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>📝 项目信息</h2>
        <div class="info-grid">
          <div class="info-item">
            <strong>项目名称</strong>
            <p>AI Agent Starter</p>
          </div>
          <div class="info-item">
            <strong>技术栈</strong>
            <p>Vue3 + FastAPI + Docker</p>
          </div>
          <div class="info-item">
            <strong>当前状态</strong>
            <p>环境就绪 🎉</p>
          </div>
          <div class="info-item">
            <strong>下一步</strong>
            <p>Day 2: 前端技术强化</p>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>🔗 快速链接</h2>
        <div class="links">
          <a href="/docs" target="_blank" class="link-button">
            📚 API 文档
          </a>
          <a href="/health" target="_blank" class="link-button">
            ❤️ 健康检查
          </a>
        </div>
      </section>
    </main>

    <footer class="footer">
      <p>Made with ❤️ for AI Agent Development Journey</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const apiStatus = ref(false)

onMounted(async () => {
  try {
    const response = await fetch('/health')
    if (response.ok) {
      apiStatus.value = true
    }
  } catch (error) {
    console.log('API 未连接（这是正常的，如果只运行前端）')
  }
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #333;
}

.header {
  text-align: center;
  padding: 3rem 1rem;
  color: white;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
}

.main-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  gap: 1.5rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
}

.card h2 {
  margin-bottom: 1.5rem;
  color: #667eea;
  font-size: 1.5rem;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.label {
  font-weight: 600;
  color: #555;
}

.value {
  font-weight: 600;
}

.value.success {
  color: #28a745;
}

.value.loading {
  color: #ffc107;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item strong {
  display: block;
  color: #667eea;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.info-item p {
  color: #555;
  line-height: 1.6;
}

.links {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.link-button {
  flex: 1;
  min-width: 150px;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  text-align: center;
  font-weight: 600;
  transition: all 0.3s ease;
}

.link-button:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.footer {
  text-align: center;
  padding: 2rem;
  color: white;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .main-content {
    padding: 1rem;
  }
  
  .card {
    padding: 1.5rem;
  }
}
</style>
