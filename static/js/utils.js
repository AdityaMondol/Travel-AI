/**
 * Logging utility that replaces console.log in production
 * Provides better error tracking and can be disabled in production
 */

const LOG_LEVELS = {
    ERROR: 'error',
    WARN: 'warn',
    INFO: 'info',
    DEBUG: 'debug'
};

class Logger {
    constructor() {
        this.isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        this.enabled = this.isDevelopment;
    }

    error(message, ...args) {
        if (this.enabled || !this.isDevelopment) {
            console.error(`[ERROR] ${message}`, ...args);
            // In production, send to error tracking service
            this.sendToTracking(LOG_LEVELS.ERROR, message, args);
        }
    }

    warn(message, ...args) {
        if (this.enabled) {
            console.warn(`[WARN] ${message}`, ...args);
        }
    }

    info(message, ...args) {
        if (this.enabled) {
            console.info(`[INFO] ${message}`, ...args);
        }
    }

    debug(message, ...args) {
        if (this.enabled) {
            console.log(`[DEBUG] ${message}`, ...args);
        }
    }

    sendToTracking(level, message, args) {
        // Placeholder for error tracking service integration
        // Could send to Sentry, LogRocket, etc.
        if (!this.isDevelopment) {
            // Example: Send to backend for logging
            try {
                fetch('/api/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        level,
                        message,
                        args,
                        timestamp: new Date().toISOString(),
                        userAgent: navigator.userAgent,
                        url: window.location.href
                    })
                }).catch(() => { }); // Fail silently
            } catch (e) {
                // Fail silently
            }
        }
    }
}

// Export singleton instance
const logger = new Logger();


/**
 * Toast Notification System
 * Shows temporary messages to users
 */
class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.init();
    }

    init() {
        // Create toast container
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        this.container.setAttribute('role', 'region');
        this.container.setAttribute('aria-label', 'Notifications');
        this.container.setAttribute('aria-live', 'polite');
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', duration = 5000) {
        const toast = this.createToast(message, type);
        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Auto dismiss
        setTimeout(() => {
            this.dismiss(toast);
        }, duration);

        return toast;
    }

    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast ${type} fade-in`;
        toast.setAttribute('role', 'status');
        toast.setAttribute('aria-live', 'polite');

        const icon = this.getIcon(type);

        toast.innerHTML = `
            <i data-lucide="${icon}" class="w-5 h-5"></i>
            <span class="flex-1">${this.escapeHtml(message)}</span>
            <button onclick="toastManager.dismiss(this.parentElement)" class="btn-ghost p-1 rounded" aria-label="Close notification">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        `;

        // Initialize icons
        setTimeout(() => {
            if (typeof lucide !== 'undefined') {
                lucide.createIcons({ icons: toast });
            }
        }, 0);

        return toast;
    }

    getIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'alert-circle',
            warning: 'alert-triangle',
            info: 'info'
        };
        return icons[type] || 'info';
    }

    dismiss(toast) {
        if (!toast || !toast.parentElement) return;

        toast.classList.add('toast-exit');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
            const index = this.toasts.indexOf(toast);
            if (index > -1) {
                this.toasts.splice(index, 1);
            }
        }, 300);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Export singleton instance
const toastManager = new ToastManager();


/**
 * Debounce function to limit function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}


/**
 * Throttle function to limit function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}


/**
 * Lazy load images with Intersection Observer
 */
class LazyLoader {
    constructor() {
        this.observer = null;
        this.init();
    }

    init() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadImage(entry.target);
                        this.observer.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px'
            });
        }
    }

    observe(img) {
        if (this.observer) {
            this.observer.observe(img);
        } else {
            // Fallback for browsers without IntersectionObserver
            this.loadImage(img);
        }
    }

    loadImage(img) {
        const src = img.dataset.src;
        if (src) {
            img.src = src;
            img.removeAttribute('data-src');
            img.classList.add('loaded');
        }
    }

    observeAll(selector = 'img[data-src]') {
        const images = document.querySelectorAll(selector);
        images.forEach(img => this.observe(img));
    }
}

const lazyLoader = new LazyLoader();


/**
 * Performance monitoring
 */
const performanceMonitor = {
    marks: {},

    start(name) {
        this.marks[name] = performance.now();
    },

    end(name) {
        if (this.marks[name]) {
            const duration = performance.now() - this.marks[name];
            logger.debug(`Performance [${name}]: ${duration.toFixed(2)}ms`);
            delete this.marks[name];
            return duration;
        }
        return null;
    }
};
