class AnalyticsDashboard {
    constructor(data) {
        this.data = data;
        this.charts = {};
        this.initializeCharts();
        this.setupEventListeners();
    }

    initializeCharts() {
        this.createDeviceChart();
        this.createProductsChart();
        this.createSearchChart();
        this.createBehaviorChart();
    }

    createDeviceChart() {
        const ctx = document.getElementById('deviceChart').getContext('2d');
        this.charts.device = new Chart(ctx, {
            type: 'doughnut',
            data: this.transformDeviceData(),
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
    }

    transformDeviceData() {
        return {
            labels: this.data.page_views.map(item => item.device_type),
            datasets: [{
                data: this.data.page_views.map(item => item.count),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56'
                ]
            }]
        };
    }

    setupEventListeners() {
        document.getElementById('startDate').addEventListener('change', () => this.updateData());
        document.getElementById('endDate').addEventListener('change', () => this.updateData());
    }

    async updateData() {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        try {
            const response = await fetch(`/api/analytics/dashboard-data/?start_date=${startDate}&end_date=${endDate}`);
            const newData = await response.json();
            this.data = newData;
            this.updateCharts();
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    updateCharts() {
        Object.keys(this.charts).forEach(chartKey => {
            const updateMethod = `update${chartKey.charAt(0).toUpperCase() + chartKey.slice(1)}Chart`;
            if (this[updateMethod]) {
                this[updateMethod]();
            }
        });
    }
}

function initializeDashboard(data) {
    window.dashboard = new AnalyticsDashboard(data);
}
