<template>
  <li :class="['todo-item', { completed: todo.completed }]">
    <!-- 复选框 -->
    <button 
      class="checkbox" 
      @click="$emit('toggle', todo.id)"
      :aria-label="todo.completed ? '标记为未完成' : '标记为已完成'"
    >
      <span v-if="todo.completed">✓</span>
    </button>

    <!-- 文本内容 -->
    <span class="text">{{ todo.text }}</span>

    <!-- 删除按钮 -->
    <button 
      class="delete-btn"
      @click="$emit('delete', todo.id)"
      aria-label="删除待办事项"
    >
      ×
    </button>
  </li>
</template>

<script setup>
defineProps({
  todo: {
    type: Object,
    required: true
  }
})

defineEmits(['toggle', 'delete'])
</script>

<style scoped>
.todo-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: rgba(255,255,255,0.95);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
}

.todo-item:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.todo-item.completed {
  background: rgba(240, 248, 255, 0.95);
}

.todo-item.completed .text {
  text-decoration: line-through;
  opacity: 0.6;
}

.checkbox {
  width: 28px;
  height: 28px;
  border: 2px solid #ddd;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.3s;
  flex-shrink: 0;
  color: white;
  font-weight: bold;
}

.checkbox:hover {
  border-color: #667eea;
  transform: scale(1.1);
}

.todo-item.completed .checkbox {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.text {
  flex: 1;
  font-size: 1rem;
  line-height: 1.5;
  color: #333;
  word-break: break-word;
}

.delete-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #ff6b6b;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s;
  flex-shrink: 0;
}

.todo-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #ee5a52;
  transform: scale(1.15);
}
</style>
