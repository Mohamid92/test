class InteractiveAnalytics {
    constructor() {
        this.heatmapData = [];
        this.interactionData = {
            startTime: Date.now(),
            clicks: 0,
            maxScroll: 0,
            interactions: []
        };
        this.setupTracking();
    }

    setupTracking() {
        // Heatmap tracking
        document.addEventListener('click', (e) => {
            this.recordClick(e);
        });

        // Scroll depth tracking
        window.addEventListener('scroll', this.throttle(() => {
            this.trackScrollDepth();
        }, 500));

        // Track form interactions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.trackFormSubmission(e);
            });
        });

        // Track element visibility
        this.setupIntersectionObserver();

        // Save data before user leaves
        window.addEventListener('beforeunload', () => {
            this.saveInteractionData();
        });
    }

    recordClick(event) {
        const clickData = {
            x: event.pageX,
            y: event.pageY,
            timestamp: Date.now(),
            element: event.target.tagName,
            path: this.getElementPath(event.target)
        };
        this.heatmapData.push(clickData);
        this.interactionData.clicks++;
    }

    trackScrollDepth() {
        const scrollDepth = (window.pageYOffset + window.innerHeight) / document.documentElement.scrollHeight * 100;
        this.interactionData.maxScroll = Math.max(this.interactionData.maxScroll, scrollDepth);
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.trackElementVisibility(entry.target);
                }
            });
        });

        document.querySelectorAll('[data-track-visibility]').forEach(element => {
            observer.observe(element);
        });
    }

    async saveInteractionData() {
        const data = {
            heatmap: this.heatmapData,
            interactions: {
                ...this.interactionData,
                totalTime: Date.now() - this.interactionData.startTime,
                url: window.location.href,
                deviceType: this.getDeviceType()
            }
        };

        try {
            await fetch('/api/analytics/interaction/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
        } catch (error) {
            console.error('Error saving interaction data:', error);
        }
    }

    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }

    getDeviceType() {
        const ua = navigator.userAgent;
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            return 'tablet';
        }
        if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
            return 'mobile';
        }
        return 'desktop';
    }

    getElementPath(element) {
        const path = [];
        while (element && element.nodeType === Node.ELEMENT_NODE) {
            let selector = element.nodeName.toLowerCase();
            if (element.id) {
                selector += `#${element.id}`;
            } else if (element.className) {
                selector += `.${element.className.replace(/\s+/g, '.')}`;
            }
            path.unshift(selector);
            element = element.parentNode;
        }
        return path.join(' > ');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.interactiveAnalytics = new InteractiveAnalytics();
});
