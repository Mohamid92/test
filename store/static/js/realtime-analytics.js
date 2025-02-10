class RealtimeAnalytics {
    constructor() {
        this.socket = null;
        this.connectWebSocket();
        this.initializeCounters();
    }

    connectWebSocket() {
        this.socket = new WebSocket(
            `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/analytics/`
        );

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
    }

    initializeCounters() {
        this.fetchInitialData();
        // Update counters every minute
        setInterval(() => this.fetchInitialData(), 60000);
    }

    async fetchInitialData() {
        try {
            const response = await fetch('/api/analytics/realtime/');
            const data = await response.json();
            this.updateCounters(data);
        } catch (error) {
            console.error('Error fetching initial data:', error);
        }
    }

    handleWebSocketMessage(data) {
        switch(data.type) {
            case 'page_view':
                this.addActivityItem(data);
                this.incrementCounter('page-views');
                break;
            case 'cart_update':
                this.updateCartCounter(data);
                break;
            case 'sale':
                this.updateSalesCounter(data);
                this.addActivityItem(data);
                break;
        }
    }

    addActivityItem(data) {
        const feed = document.getElementById('activity-feed');
        const item = document.createElement('div');
        item.className = 'p-2 border-b border-gray-200';
        item.innerHTML = this.getActivityHTML(data);
        feed.insertBefore(item, feed.firstChild);

        // Limit the number of items
        if (feed.children.length > 20) {
            feed.removeChild(feed.lastChild);
        }
    }

    getActivityHTML(data) {
        switch(data.type) {
            case 'page_view':
                return `<span class="text-blue-600">👀</span> Someone is viewing ${data.page}`;
            case 'sale':
                return `<span class="text-green-600">💰</span> New sale: QAR ${data.amount}`;
            default:
                return '';
        }
    }

    updateCounters(data) {
        document.getElementById('active-users').textContent = data.active_users;
        document.getElementById('page-views').textContent = data.page_views;
        document.getElementById('active-carts').textContent = data.active_carts;
        document.getElementById('today-sales').textContent = `QAR ${data.today_sales}`;
    }
}

// Initialize realtime analytics
document.addEventListener('DOMContentLoaded', () => {
    new RealtimeAnalytics();
});
