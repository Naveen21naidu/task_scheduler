let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

function saveTasks() {
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

function addTask(name, dueDate) {
  tasks.push({
    id: Date.now(),
    name,
    dueDate,
    status: 'pending'
  });
  saveTasks();
  renderTasks();
}

function deleteTask(id) {
  tasks = tasks.filter(t => t.id !== id);
  saveTasks();
  renderTasks();
}

function completeTask(id) {
  tasks = tasks.map(t => t.id === id ? { ...t, status: 'completed' } : t);
  saveTasks();
  renderTasks();
}

function undoTask(id) {
  tasks = tasks.map(t => t.id === id ? { ...t, status: 'pending' } : t);
  saveTasks();
  renderTasks();
}

function renderTasks() {
  const container = document.getElementById('task-list');
  container.innerHTML = '';

  if (tasks.length === 0) {
    container.innerHTML = `<div class="no-tasks">🎉 No tasks yet! Click below to add one.</div>`;
    return;
  }

  tasks.forEach(task => {
    const statusClass =
      task.status === 'completed' ? 'status-completed' :
      task.status === 'overdue' ? 'status-overdue' :
      'status-pending';

    const statusLabel =
      task.status === 'completed' ? '✅ Completed' :
      task.status === 'overdue' ? '⚠️ Overdue' :
      '⏳ Pending';

    const taskDiv = document.createElement('div');
    taskDiv.className = 'task-container';
    taskDiv.innerHTML = `
      <div class="task-title">${task.name}</div>
      <div class="task-date">Due: ${formatDate(task.dueDate)}</div>
      <div class="status-label ${statusClass}">
        ${statusLabel}
        ${task.status === 'completed' ? `
          <button class="btn-undo" onclick="undoTask(${task.id})">Undo</button>
        ` : ''}
      </div>
      <div class="btn-group">
        ${task.status !== 'completed' ? `
          <button class="btn btn-complete" onclick="completeTask(${task.id})">Complete</button>
        ` : ''}
        <button class="btn btn-delete" onclick="deleteTask(${task.id})">Delete</button>
      </div>
    `;
    container.appendChild(taskDiv);
  });
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  const options = {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  };
  return date.toLocaleString('en-IN', options);
}

function handleAdd(e) {
  e.preventDefault();
  const name = document.getElementById('taskName').value;
  const due = document.getElementById('dueDate').value;
  if (name && due) {
    addTask(name, due);
    document.getElementById('taskName').value = '';
    document.getElementById('dueDate').value = '';
  }
}
