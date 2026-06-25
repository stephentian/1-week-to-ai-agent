# Day 2 实战项目：待办事项管理应用 (TodoApp)

> **项目名称**: vue3-todo-app
> **项目描述**: 使用Vue3 Composition API构建的现代化待办事项管理应用
> **技术栈**: Vue3 + Vite + Pinia + CSS3

---

## 📁 项目结构

```
todo-app/
├── src/
│   ├── main.js                 # 应用入口
│   ├── App.vue                 # 根组件
│   ├── components/            # 组件目录
│   │   └── TodoItem.vue        # 单个待办项组件
│   └── composables/           # 组合式函数
│       └── useTodo.js          # 待办事项逻辑
├── index.html                  # HTML模板
├── package.json               # 项目配置
├── vite.config.js             # Vite配置
└── README.md                  # 项目说明
```

---

## 🚀 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

访问`http://localhost:5173` 查看应用

---

## ✅ 功能清单

### 核心功能
- [x] 添加待办事项（输入框+按钮）
- [x] 标记完成/未完成（点击切换）
- [x] 删除待办事项
- [x] 筛选显示（全部/已完成/未完成）
- [x] 本地持久化（localStorage）
- [x] 统计信息显示
- [x] 批量清除已完成项
- [x] 过渡动画效果

### 技术特性
- [x] Vue3 Composition API (`<script setup>`)
- [x] 响应式数据管理 (`ref`,`computed`,`watch`)
- [x] 组合式函数模式 (Composables)
- [x] 列表过渡动画 (`<transition-group>`)
- [x] 本地存储持久化
- [x] 响应式布局设计

---

## 📝 技术要点

### 1. Composition API 使用
```vue
<script setup>
import { ref, computed } from 'vue'

const todos = ref([])
const filter = ref('all')

const filteredTodos = computed(() => {
  // 计算属性实现筛选逻辑
})
</script>
```

### 2. Composable 模式
```javascript
// composables/useTodo.js
export function useTodo() {
  const todos = ref([])
  
  const addTodo = (text) => { /* ... */ }
  const toggleTodo = (id) => { /* ... */ }
  const deleteTodo = (id) => { /* ... */ }
  
  return { todos, addTodo, toggleTodo, deleteTodo }
}
```

### 3. localStorage 持久化
```javascript
// 使用 watch 监听变化并自动保存
watch(todos, (newVal) => {
  localStorage.setItem('todos', JSON.stringify(newVal))
}, { deep: true })
```

---

## 🔗 相关文档

本项目对应 **Day 2** 的以下学习内容：
- HTML5语义化标签
- CSS Flexbox/Grid布局
- JavaScript ES6+特性
- Vue3 Composition API
- 组件通信与状态管理

**下一步**: [Day 3: 后端开发技能提升](../03-后端开发技能提升/README.md)
