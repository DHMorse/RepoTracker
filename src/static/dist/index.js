"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Handle moving a repo up in priority order
 */
function handleMoveUp(event) {
    var _a;
    const button = event.currentTarget;
    const repoElement = button.closest('.repo');
    if (!repoElement)
        return;
    const repoId = repoElement.dataset.repoId;
    const previousRepo = repoElement.previousElementSibling;
    // If there's no previous repo (already at top) or if previous element is not a repo, do nothing
    if (!previousRepo || !previousRepo.classList.contains('repo'))
        return;
    const previousRepoId = previousRepo.dataset.repoId;
    const previousRepoOrder = getRepoOrder(previousRepo);
    const currentRepoOrder = getRepoOrder(repoElement);
    // Swap the visual order
    (_a = repoElement.parentNode) === null || _a === void 0 ? void 0 : _a.insertBefore(repoElement, previousRepo);
    // Send API requests to update both repos
    updateRepoOrder(repoId, previousRepoOrder);
    updateRepoOrder(previousRepoId, currentRepoOrder);
}
/**
 * Handle moving a repo down in priority order
 */
function handleMoveDown(event) {
    var _a;
    const button = event.currentTarget;
    const repoElement = button.closest('.repo');
    if (!repoElement)
        return;
    const repoId = repoElement.dataset.repoId;
    const nextRepo = repoElement.nextElementSibling;
    // If there's no next repo (already at bottom) or if next element is not a repo, do nothing
    if (!nextRepo || !nextRepo.classList.contains('repo'))
        return;
    const nextRepoId = nextRepo.dataset.repoId;
    const nextRepoOrder = getRepoOrder(nextRepo);
    const currentRepoOrder = getRepoOrder(repoElement);
    // Swap the visual order
    (_a = repoElement.parentNode) === null || _a === void 0 ? void 0 : _a.insertBefore(nextRepo, repoElement);
    // Send API requests to update both repos
    updateRepoOrder(repoId, nextRepoOrder);
    updateRepoOrder(nextRepoId, currentRepoOrder);
}
/**
 * Get the priority order of a repo element
 * This is an estimate based on position in the DOM
 */
function getRepoOrder(repoElement) {
    let position = 0;
    let element = repoElement;
    while (element.previousElementSibling) {
        if (element.previousElementSibling.classList.contains('repo')) {
            position++;
        }
        element = element.previousElementSibling;
    }
    return position;
}
/**
 * Send API request to update a repo's priority order
 */
function updateRepoOrder(repoId, priorityOrder) {
    if (!repoId)
        return;
    fetch('/api/repos/reorder', {
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
            throw new Error('Failed to update repo order');
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
function handleEditRepo(event) {
    var _a, _b, _c, _d, _e, _f, _g, _h;
    const button = event.currentTarget;
    const repoElement = button.closest('.repo');
    if (!repoElement)
        return;
    // Get current repo data
    const repoId = repoElement.dataset.repoId;
    const repoName = ((_a = repoElement.querySelector('.repo-name')) === null || _a === void 0 ? void 0 : _a.textContent) || '';
    const progressValue = parseInt(((_d = (_c = (_b = repoElement.querySelector('.progress')) === null || _b === void 0 ? void 0 : _b.getAttribute('style')) === null || _c === void 0 ? void 0 : _c.match(/width:\s*(\d+)%/)) === null || _d === void 0 ? void 0 : _d[1]) || '0');
    const milestone = ((_f = (_e = repoElement.querySelector('.next-milestone')) === null || _e === void 0 ? void 0 : _e.textContent) === null || _f === void 0 ? void 0 : _f.replace('Next milestone: ', '')) || '';
    const timeRequired = ((_h = (_g = repoElement.querySelector('.time-required')) === null || _g === void 0 ? void 0 : _g.textContent) === null || _h === void 0 ? void 0 : _h.replace('- Time required: ', '')) || '';
    // Create the edit modal
    createEditRepoModal(repoElement, {
        id: repoId || '',
        name: repoName,
        progress: progressValue,
        milestone,
        timeRequired
    });
}
function createEditRepoModal(repoElement, repoData) {
    // Check if a modal is already open and remove it
    const existingModal = document.querySelector('.edit-repo-modal');
    if (existingModal) {
        existingModal.remove();
    }
    // Determine current priority based on parent section
    const section = repoElement.closest('.section');
    const sectionTitle = section === null || section === void 0 ? void 0 : section.querySelector('.section-title');
    let currentPriority = 'medium';
    if (sectionTitle === null || sectionTitle === void 0 ? void 0 : sectionTitle.classList.contains('high-priority-title')) {
        currentPriority = 'high';
    }
    else if (sectionTitle === null || sectionTitle === void 0 ? void 0 : sectionTitle.classList.contains('low-priority-title')) {
        currentPriority = 'low';
    }
    // Create modal container
    const modalContainer = document.createElement('div');
    modalContainer.className = 'edit-repo-modal';
    // Create modal content
    modalContainer.innerHTML = `
        <div class="edit-repo-modal-content">
            <h3>Edit Repo: ${repoData.name}</h3>
            
            <div class="form-group">
                <label for="repo-priority">Priority:</label>
                <select id="repo-priority">
                    <option value="high" ${currentPriority === 'high' ? 'selected' : ''}>High Priority</option>
                    <option value="medium" ${currentPriority === 'medium' ? 'selected' : ''}>Medium Priority</option>
                    <option value="low" ${currentPriority === 'low' ? 'selected' : ''}>Low Priority</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="repo-progress">Progress:</label>
                <div class="progress-input-group">
                    <input type="range" id="repo-progress-slider" min="0" max="100" value="${repoData.progress}" class="progress-slider">
                    <input type="number" id="repo-progress-number" min="0" max="100" value="${repoData.progress}" class="progress-number">
                    <span class="progress-percent">%</span>
                </div>
            </div>
            
            <div class="form-group">
                <label for="repo-milestone">Next Milestone:</label>
                <input type="text" id="repo-milestone" value="${repoData.milestone}">
            </div>
            
            <div class="form-group">
                <label for="repo-time">Time Required:</label>
                <input type="text" id="repo-time" value="${repoData.timeRequired}">
            </div>
            
            <div class="button-group">
                <button id="save-repo-button">Save</button>
                <button id="cancel-repo-button">Cancel</button>
            </div>
        </div>
    `;
    // Add the modal to the document
    document.body.appendChild(modalContainer);
    // Add event listeners to the form controls
    setupModalEventListeners(modalContainer, repoData.id);
}
/**
 * Setup event listeners for the modal form
 */
function setupModalEventListeners(modalContainer, repoId) {
    // Sync the progress slider and number input
    const progressSlider = modalContainer.querySelector('#repo-progress-slider');
    const progressNumber = modalContainer.querySelector('#repo-progress-number');
    progressSlider.addEventListener('input', () => {
        progressNumber.value = progressSlider.value;
    });
    progressNumber.addEventListener('input', () => {
        // Ensure value is between 0 and 100
        let value = parseInt(progressNumber.value);
        if (isNaN(value))
            value = 0;
        if (value < 0)
            value = 0;
        if (value > 100)
            value = 100;
        progressSlider.value = value.toString();
    });
    // Close modal on cancel
    const cancelButton = modalContainer.querySelector('#cancel-repo-button');
    cancelButton === null || cancelButton === void 0 ? void 0 : cancelButton.addEventListener('click', () => {
        modalContainer.remove();
    });
    // Save changes on save button click
    const saveButton = modalContainer.querySelector('#save-repo-button');
    saveButton === null || saveButton === void 0 ? void 0 : saveButton.addEventListener('click', () => {
        const priority = modalContainer.querySelector('#repo-priority').value;
        const progress = parseInt(modalContainer.querySelector('#repo-progress-number').value);
        const milestone = modalContainer.querySelector('#repo-milestone').value;
        const timeRequired = modalContainer.querySelector('#repo-time').value;
        // Call function to save the changes
        saveRepoChanges(repoId, {
            priority,
            progress,
            milestone,
            timeRequired
        });
        // Close the modal
        modalContainer.remove();
    });
}
function saveRepoChanges(repoId, changes) {
    // Check if repoId exists
    if (!repoId || repoId === 'undefined' || repoId === 'null') {
        console.error('Invalid repo ID:', repoId);
        alert('Cannot update repo: Invalid repo ID');
        return;
    }
    // Create a promise to handle both real and mock API paths
    const updatePromise = new Promise((resolve, reject) => {
        // Check if API endpoint exists by sending a preflight request
        fetch('/api/repos/update', { method: 'OPTIONS' })
            .then(response => {
            if (!response.ok) {
                throw new Error('API endpoint not available');
            }
            // If the preflight check passed, send the real API request
            return fetch('/api/repos/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(Object.assign({ repoId: parseInt(repoId) }, changes))
            });
        })
            .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update repo');
            }
            return response.json();
        })
            .then(data => {
            console.log('Repo updated successfully:', data);
            resolve();
        })
            .catch(error => {
            // If the API doesn't exist or fails, simulate success for testing
            if (error.message === 'API endpoint not available') {
                console.warn('API endpoint not found. Using mock response for development.');
                // Show the changes that would be sent
                console.log('Repo update data:', Object.assign({ repoId: parseInt(repoId) }, changes));
                // Simulate successful update
                setTimeout(() => {
                    console.log('Repo updated successfully (mock)');
                    resolve();
                }, 500);
            }
            else {
                console.error('Error updating repo:', error);
                reject(error);
            }
        });
    });
    // Handle the update promise result
    updatePromise
        .then(() => {
        // Refresh the page to show updated repo data
        window.location.reload();
    })
        .catch(error => {
        alert('Failed to update repo. Please try again.');
    });
}
/**
 * Handle opening the .repoignore editor modal
 */
function handleEditRepoignore(event) {
    // Fetch current .repoignore content
    fetch('/api/repoignore')
        .then(response => response.text())
        .then(content => {
        const modal = document.getElementById('edit-repoignore-modal');
        const textarea = document.getElementById('repoignore-content');
        if (modal && textarea) {
            textarea.value = content;
            modal.style.display = 'flex';
        }
    })
        .catch(error => {
        console.error('Error fetching .repoignore content:', error);
    });
}
/**
 * Handle saving changes to the .repoignore file
 */
function handleSaveRepoignore(event) {
    const textarea = document.getElementById('repoignore-content');
    if (!textarea)
        return;
    const content = textarea.value;
    fetch('/api/repoignore', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: content
    })
        .then(response => {
        if (!response.ok) {
            throw new Error('Failed to save .repoignore');
        }
        handleCancelRepoignore(event);
        // Reload the page to reflect changes
        window.location.reload();
    })
        .catch(error => {
        console.error('Error saving .repoignore:', error);
    });
}
/**
 * Handle closing the .repoignore editor modal
 */
function handleCancelRepoignore(event) {
    const modal = document.getElementById('edit-repoignore-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}
/**
 * Handle refreshing the repos
 */
function handleRefreshRepos(event) {
    // Create a loading animation on the button
    const button = event.currentTarget;
    if (button) {
        const icon = button.querySelector('i');
        if (icon) {
            icon.classList.add('fa-spin');
        }
        button.disabled = true;
    }
    // Call the refresh API endpoint
    fetch('/api/repos/refresh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => {
        if (!response.ok) {
            throw new Error('Failed to refresh repos');
        }
        return response.json();
    })
        .then(data => {
        console.log('Success:', data);
        // Reload the page to show updated repo data
        window.location.reload();
    })
        .catch(error => {
        console.error('Error:', error);
        // Remove the animation and re-enable the button
        if (button) {
            const icon = button.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-spin');
            }
            button.disabled = false;
        }
        alert('Failed to refresh repos. Please try again.');
    });
}
// Assign functions to window object to make them accessible from HTML
window.handleMoveUp = handleMoveUp;
window.handleMoveDown = handleMoveDown;
window.handleEditRepo = handleEditRepo;
window.handleEditRepoignore = handleEditRepoignore;
window.handleSaveRepoignore = handleSaveRepoignore;
window.handleCancelRepoignore = handleCancelRepoignore;
window.handleRefreshRepos = handleRefreshRepos;
// We still need the DOMContentLoaded event for any initialization that should happen
// when the page loads, but not for setting up event handlers for the buttons
document.addEventListener('DOMContentLoaded', () => {
    // Any other initialization code can go here
    console.log('DOM loaded and ready!');
});
