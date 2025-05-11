/**
 * NewsNow - Main JavaScript file
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check for dark mode preference
    initDarkMode();
    
    // Initialize tooltips
    initTooltips();
});

/**
 * Initialize dark mode
 */
function initDarkMode() {
    // Check for system preference
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Check for saved preference
    const savedMode = localStorage.getItem('darkMode');
    
    // Apply dark mode if preferred or saved
    if (savedMode === 'true' || (savedMode === null && prefersDarkMode)) {
        document.body.classList.add('dark-mode');
    }
    
    // Add dark mode toggle to footer
    const footer = document.querySelector('footer .row');
    if (footer) {
        const darkModeToggle = document.createElement('div');
        darkModeToggle.className = 'col-12 mt-2 text-center';
        darkModeToggle.innerHTML = `
            <button id="dark-mode-toggle" class="btn btn-sm btn-outline-secondary">
                ${document.body.classList.contains('dark-mode') ? 'Light Mode' : 'Dark Mode'}
            </button>
        `;
        footer.appendChild(darkModeToggle);
        
        // Add event listener
        document.getElementById('dark-mode-toggle').addEventListener('click', toggleDarkMode);
    }
}

/**
 * Toggle dark mode
 */
function toggleDarkMode() {
    const isDarkMode = document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
    
    // Update button text
    const button = document.getElementById('dark-mode-toggle');
    if (button) {
        button.textContent = isDarkMode ? 'Light Mode' : 'Dark Mode';
    }
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Format relative time
 * @param {string} dateStr - Date string to format
 * @returns {string} Formatted relative time
 */
function formatRelativeTime(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // Difference in seconds
    
    if (diff < 60) {
        return `${diff} second${diff !== 1 ? 's' : ''} ago`;
    } else if (diff < 3600) {
        const minutes = Math.floor(diff / 60);
        return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (diff < 86400) {
        const hours = Math.floor(diff / 3600);
        return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else if (diff < 604800) {
        const days = Math.floor(diff / 86400);
        return `${days} day${days !== 1 ? 's' : ''} ago`;
    } else if (diff < 2592000) {
        const weeks = Math.floor(diff / 604800);
        return `${weeks} week${weeks !== 1 ? 's' : ''} ago`;
    } else if (diff < 31536000) {
        const months = Math.floor(diff / 2592000);
        return `${months} month${months !== 1 ? 's' : ''} ago`;
    } else {
        const years = Math.floor(diff / 31536000);
        return `${years} year${years !== 1 ? 's' : ''} ago`;
    }
}

/**
 * Truncate text to a specific length
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, length = 100) {
    if (!text) return '';
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
} 