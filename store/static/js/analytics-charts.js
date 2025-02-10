class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.initializeDateRange();
        this.initializeCharts();
    }

    initializeDateRange() {
        const dateRange = document.getElementById('dateRange');
        if (dateRange) {
            dateRange.addEventListener('change', (e) => {
                const [start, end] = e.target.value.split(' to ');
                this.updateCharts(start, end);
            });
        }
    }

    async updateCharts(startDate, endDate) {
        const data = await this.fetchData(startDate, endDate);
        Object.keys(this.charts).forEach(chartId => {
            const updateMethod = `update${chartId}Chart`;
            if (this[updateMethod]) {
                this[updateMethod](data);
            }
        });
    }

    initializeCharts() {
        // Revenue Chart
        this.createRevenueChart();
        // Transactions Chart
        this.createTransactionsChart();
        // Payment Methods Chart
        this.createPaymentMethodsChart();
    }

    createRevenueChart() {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        this.charts.revenue = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Daily Revenue',
                    borderColor: '#3498db',
                    fill: true,
                    data: []
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: value => `QAR ${value}`
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: context => `QAR ${context.parsed.y}`
                        }
                    }
                }
            }
        });
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsDashboard();
});
