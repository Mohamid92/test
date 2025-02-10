class BehaviorTracker {
    constructor() {
        this.queue = [];
        this.queueLimit = 10;
        this.flushInterval = 5000; // 5 seconds
        this.setupEventListeners();
        this.startQueueProcessing();
    }

    setupEventListeners() {
        // Click tracking
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-track]');
            if (target) {
                this.trackEvent('CLICK', {
                    element: target.dataset.track,
                    text: target.textContent,
                    path: target.dataset.trackPath || null
                });
            }
        });

        // Scroll tracking
        let scrollTimeout;
        document.addEventListener('scroll', () => {
            if (scrollTimeout) clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.trackEvent('SCROLL', {
                    depth: this.getScrollDepth(),
                    pageHeight: document.documentElement.scrollHeight
                });
            }, 150);
        });

        // Search tracking
        const searchForm = document.querySelector('[data-track-search]');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                this.trackEvent('SEARCH', {
                    query: searchForm.querySelector('input').value,
                    category: searchForm.dataset.category || null
                });
            });
        }
    }

    trackEvent(type, data) {
        this.queue.push({
            type,
            data,
            timestamp: new Date().toISOString(),
            url: window.location.href
        });

        if (this.queue.length >= this.queueLimit) {
            this.flushQueue();
        }
    }

    async flushQueue() {
        if (!this.queue.length) return;

        const events = [...this.queue];
        this.queue = [];

        try {
            await fetch('/api/analytics/track/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ events })
            });
        } catch (error) {
            console.error('Error sending analytics:', error);
            // Restore failed events to queue
            this.queue = [...events, ...this.queue];
        }
    }

    startQueueProcessing() {
        setInterval(() => this.flushQueue(), this.flushInterval);
    }

    getScrollDepth() {
        const winHeight = window.innerHeight;
        const docHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset;
        return Math.round((scrollTop + winHeight) / docHeight * 100);
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
}

// Initialize tracker
document.addEventListener('DOMContentLoaded', () => {
    window.behaviorTracker = new BehaviorTracker();
});
