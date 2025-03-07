document.addEventListener('DOMContentLoaded', () => {
    // Get all move up and move down buttons
    const moveUpButtons = document.querySelectorAll('.move-up');
    const moveDownButtons = document.querySelectorAll('.move-down');

    // Add event listeners to move up buttons
    moveUpButtons.forEach(button => {
        button.addEventListener('click', handleMoveUp);
    });

    // Add event listeners to move down buttons
    moveDownButtons.forEach(button => {
        button.addEventListener('click', handleMoveDown);
    });
});

/**
 * Handle moving a task up in priority order
 */
function handleMoveUp(event: Event): void {
    const button = event.currentTarget as HTMLButtonElement;
    const taskElement = button.closest('.task') as HTMLElement;
    
    if (!taskElement) return;
    
    const taskId = taskElement.dataset.taskId;
    const previousTask = taskElement.previousElementSibling as HTMLElement;
    
    // If there's no previous task (already at top) or if previous element is not a task, do nothing
    if (!previousTask || !previousTask.classList.contains('task')) return;
    
    const previousTaskId = previousTask.dataset.taskId;
    const previousTaskOrder = getTaskOrder(previousTask);
    const currentTaskOrder = getTaskOrder(taskElement);
    
    // Swap the visual order
    taskElement.parentNode?.insertBefore(taskElement, previousTask);
    
    // Send API requests to update both tasks
    updateTaskOrder(taskId, previousTaskOrder);
    updateTaskOrder(previousTaskId, currentTaskOrder);
}

/**
 * Handle moving a task down in priority order
 */
function handleMoveDown(event: Event): void {
    const button = event.currentTarget as HTMLButtonElement;
    const taskElement = button.closest('.task') as HTMLElement;
    
    if (!taskElement) return;
    
    const taskId = taskElement.dataset.taskId;
    const nextTask = taskElement.nextElementSibling as HTMLElement;
    
    // If there's no next task (already at bottom) or if next element is not a task, do nothing
    if (!nextTask || !nextTask.classList.contains('task')) return;
    
    const nextTaskId = nextTask.dataset.taskId;
    const nextTaskOrder = getTaskOrder(nextTask);
    const currentTaskOrder = getTaskOrder(taskElement);
    
    // Swap the visual order
    taskElement.parentNode?.insertBefore(nextTask, taskElement);
    
    // Send API requests to update both tasks
    updateTaskOrder(taskId, nextTaskOrder);
    updateTaskOrder(nextTaskId, currentTaskOrder);
}

/**
 * Get the priority order of a task element
 * This is an estimate based on position in the DOM
 */
function getTaskOrder(taskElement: HTMLElement): number {
    let position = 0;
    let element = taskElement;
    
    while (element.previousElementSibling) {
        if (element.previousElementSibling.classList.contains('task')) {
            position++;
        }
        element = element.previousElementSibling as HTMLElement;
    }
    
    return position;
}

/**
 * Send API request to update a task's priority order
 */
function updateTaskOrder(repoId: string | undefined, priorityOrder: number): void {
    if (!repoId) return;
    
    fetch('/api/tasks/reorder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            repoId: parseInt(repoId),
            priorityOrder: priorityOrder
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to update task order');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}