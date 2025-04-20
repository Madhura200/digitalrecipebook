// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add event listeners to favorite buttons
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            const recipeId = this.getAttribute('data-recipe-id');
            console.log("Favorite button clicked for Recipe ID:", recipeId); // Debugging
            debouncedToggleFavorite(recipeId);
        });
    });

    // Add event listener to flash message close buttons
    document.querySelectorAll('.alert .btn-close').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.classList.add('fade');
            setTimeout(() => {
                this.parentElement.classList.add('d-none');
            }, 150);
        });
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.classList.add('d-none');
            }, 500);
        });
    }, 5000);
});

/**
 * Toggle a recipe favorite status
 * @param {string} recipeId - The ID of the recipe to toggle
 */
function toggleFavorite(recipeId) {
    if (!recipeId) {
        console.error("Recipe ID is undefined or null.");
        return;
    }

    console.log("Toggling favorite for Recipe ID:", recipeId); // Debugging
    const formData = new FormData();

    // Send AJAX request
    fetch(`/toggle_favorite/${recipeId}`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response received:", data); // Debugging

        if (data.status === 'success') {
            // Update all favorite buttons for this recipe
            const buttons = document.querySelectorAll(`.favorite-btn[data-recipe-id="${recipeId}"]`);
            console.log("Buttons found:", buttons); // Debugging

            buttons.forEach(button => {
                const icon = button.querySelector('i');
                icon.className = data.is_favorite ? 'fas fa-heart text-danger' : 'far fa-heart';
            });

            // Show a temporary feedback message
            showToast(
                `${data.is_favorite ? 'Added to' : 'Removed from'} favorites`,
                data.is_favorite ? 'success' : 'secondary',
                `${data.is_favorite ? 'fas' : 'far'} fa-heart`
            );
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Failed to update favorite status', 'danger', 'fas fa-exclamation-circle');
    });
}

/**
 * Show a Bootstrap toast notification
 * @param {string} message - The message to display
 * @param {string} type - The Bootstrap background color class (e.g., 'success', 'danger')
 * @param {string} iconClass - FontAwesome icon class for the toast
 */
function showToast(message, type, iconClass) {
    console.log('Showing toast:', message); // Debugging

    const feedback = document.createElement('div');
    feedback.className = 'position-fixed top-0 start-50 translate-middle-x p-3';
    feedback.style.zIndex = 1050;

    feedback.innerHTML = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="${iconClass} me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    document.body.appendChild(feedback);
    const toast = new bootstrap.Toast(feedback.querySelector('.toast'));
    toast.show();

    setTimeout(() => {
        feedback.remove();
    }, 3000);
}

/**
 * Debounce function to prevent multiple rapid clicks
 * @param {Function} func - Function to debounce
 * @param {number} delay - Time in milliseconds to delay
 * @returns {Function} - Debounced function
 */
function debounce(func, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

// Debounced version of toggleFavorite
const debouncedToggleFavorite = debounce(toggleFavorite, 500);
