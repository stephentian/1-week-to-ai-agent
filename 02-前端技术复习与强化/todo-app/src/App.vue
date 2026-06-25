<template>
  <div class="todo-app">
    <header class="header">
      <h1>📝 待办事项</h1>
      <p class="subtitle">Vue3 Composition API 实战项目</p>
    </header>

    <main class="main-content">
      <!-- 输入区域 -->
      <form @submit.prevent="addTodo" class="input-group">
        <input
          v-model="newTodo"
          type="text"
          placeholder="添加新的待办事项..."
          class="todo-input"
          autofocus
        />
        <button type="submit" class="add-btn" :disabled="!newTodo.trim()">
          添加
        </button>
      </form>

      <!-- 筛选器 -->
      <div class="filters">
        <button
          v-for="f in filterOptions"
          :key="f.value"
          :class="['filter-btn', { active: filter === f.value }]"
          @click="filter = f.value"
        >
          {{ f.label }}
          <span class="count" v-if="f.value !== 'all'">({{ getCount(f.value) }})</span>
        </button>
      </div>

      <!-- 统计信息 -->
      <div class="stats">
        <p>共 <strong>{{ totalTodos }}</strong> 项，
           已完成 <strong>{{ completedCount }}</strong> 项，
           剩余 <strong>{{ remainingCount }}</strong> 项</p>
      </div>

      <!-- 待办列表 -->
      <transition-group name="list" tag="ul" class="todo-list">
        <TodoItem
          v-for="todo in filteredTodos"
          :key="todo.id"
          :todo="todo"
          @toggle="toggleTodo"
          @delete="deleteTodo"
        />
      </transition-group>

      <!-- 空状态提示 -->
      <div v-if="filteredTodos.length === 0" class="empty-state">
        <p>😊 暂无待办事项</p>
        <p class="hint">{{ emptyMessage }}</p>
      </div>

      <!-- 清除已完成按钮 -->
      <button
        v-if="completedCount > 0"
        @click="clearCompleted"
        class="clear-btn"
      >
        清除已完成 ({{ completedCount }})
      </button>
    </main>

    <footer class="footer">
      <p>Built with Vue3 + Composition API | Day 2 实战项目</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import TodoItem from './components/TodoItem.vue'
import { useTodo } from './composables/useTodo'

const {
  todos,
  addTodo: addTodoItem,
  toggleTodo,
  deleteTodo,
  clearCompleted
} = useTodo()

const newTodo = ref('')
const filter = ref('all')

const filterOptions = [
  { value: 'all', label: '全部' },
  { value: 'active', label: '未完成' },
  { value: 'completed', label: '已完成' }
]

// 计算属性
const filteredTodos = computed(() => {
  switch (filter.value) {
    case 'active':
      return todos.value.filter(todo => !todo.completed)
    case 'completed':
      return todos.value.filter(todo => todo.completed)
    default:
      return todos.value
  }
})

const totalTodos = computed(() => todos.value.length)

const completedCount = computed(() => 
  todos.value.filter(todo => todo.completed).length
)

const remainingCount = computed(() => totalTodos.value - completedCount.value)

const emptyMessage = computed(() => {
  if (totalTodos.value === 0) {
    return '添加你的第一个待办事项吧！'
  }
  switch (filter.value) {
    case 'active': return '没有未完成的任务了，太棒了！🎉'
    case 'completed': return '还没有已完成的任务'
    default: return ''
  }
})

// 方法
function addTodo() {
  const text = newTodo.value.trim()
  if (!text) return
  
  addTodoItem(text)
  newTodo.value = ''
}

function getCount(type) {
  if (type === 'active') return remainingCount.value
  if (type === 'completed') return completedCount.value
  return 0
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.todo-app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  text-align: center;
  padding: 3rem 1rem 2rem;
  color: white;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
}

.main-content {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 1rem 3rem;
}

.input-group {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.todo-input {
  flex: 1;
  padding: 1rem;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: box-shadow 0.3s;
}

.todo-input:focus {
  outline: none;
  box-shadow: 0 6px 20px rgba(0,0,0,0.25);
}

.add-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.add-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(72, 198, 239, 0.4);
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.65rem 1.25rem;
  background: rgba(255,255,255,0.95);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  color: #555;
}

.filter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.filter-btn.active {
  background: white;
  border-color: #667eea;
  color: #667eea;
  font-weight: 600;
}

.count {
  margin-left: 0.35rem;
  font-size: 0.85rem;
  opacity: 0.7;
}

.stats {
  background: rgba(255,255,255,0.95);
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stats p {
  color: #555;
  line-height: 1.6;
}

.stats strong {
  color: #667eea;
}

.todo-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: white;
}

.empty-state p:first-child {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.hint {
  opacity: 0.85;
  font-size: 0.95rem;
}

.clear-btn {
  width: 100%;
  padding: 1rem;
  margin-top: 1.5rem;
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b6b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.clear-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 107, 107, 0.4);
}

.footer {
  text-align: center;
  padding: 2rem;
  color: white;
  opacity: 0.85;
  font-size: 0.9rem;
}

/* 列表动画 */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.list-move {
  transition: transform 0.3s ease;
}

@media (max-width: 480px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .add-btn {
    width: 100%;
  }
  
  .filters {
    justify-content: center;
  }
}
</style>
