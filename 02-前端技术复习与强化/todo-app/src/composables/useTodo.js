import { ref, computed, watch } from 'vue'

export function useTodo() {
  // 状态
  const todos = ref(JSON.parse(localStorage.getItem('todos') || '[]'))

  // 持久化：监听变化自动保存
  watch(todos, (newVal) => {
    localStorage.setItem('todos', JSON.stringify(newVal))
  }, { deep: true })

  // 方法
  function addTodo(text) {
    const todo = {
      id: Date.now(),
      text: text.trim(),
      completed: false,
      createdAt: new Date().toISOString()
    }
    todos.value.unshift(todo)
  }

  function toggleTodo(id) {
    const todo = todos.value.find(t => t.id === id)
    if (todo) {
      todo.completed = !todo.completed
    }
  }

  function deleteTodo(id) {
    todos.value = todos.value.filter(t => t.id !== id)
  }

  function clearCompleted() {
    todos.value = todos.value.filter(t => !t.completed)
  }

  return {
    todos,
    addTodo,
    toggleTodo,
    deleteTodo,
    clearCompleted
  }
}
