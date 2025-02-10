class AnalyticsDashboard {
    constructor() {
        this.initializeCharts();
        this.bindDateRangeFilter();
    }

    initializeCharts() {
        this.createTransactionsChart();
        this.createRevenueChart();
        this.createPaymentMethodsChart();
    }

    async fetchData(startDate, endDate) {
        const response = await fetch(`/api/analytics/payments/?start_date=${startDate}&end_date=${endDate}`);
        return await response.json();
    }

    createTransactionsChart() {
        const ctx = document.getElementById('transactionsChart').getContext('2d');
        this.transactionsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Successful Transactions',
                    borderColor: '#2ecc71',
                    data: []
                }, {
                    label: 'Failed Transactions',
                    borderColor: '#e74c3c',
                    data: []
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createRevenueChart() {
        const ctx = document.getElementById('revenueChart').getContext('2d');
        this.revenueChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Revenue',
                    backgroundColor: '#3498db',
                    data: []
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    createPaymentMethodsChart() {
        const ctx = document.getElementById('paymentMethodsChart').getContext('2d');
        this.methodsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#2ecc71',
                        '#3498db',
                        '#9b59b6',
                        '#f1c40f',
                        '#e74c3c'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    updateCharts(data) {
        // Update transaction chart
        this.transactionsChart.data.labels = data.dates;
        this.transactionsChart.data.datasets[0].data = data.successful_transactions;
        this.transactionsChart.data.datasets[1].data = data.failed_transactions;
        this.transactionsChart.update();

        // Update revenue chart
        this.revenueChart.data.labels = data.dates;
        this.revenueChart.data.datasets[0].data = data.revenue;
        this.revenueChart.update();

        // Update payment methods chart
        this.methodsChart.data.labels = Object.keys(data.payment_methods);
        this.methodsChart.data.datasets[0].data = Object.values(data.payment_methods);
        this.methodsChart.update();
    }

    bindDateRangeFilter() {
        const form = document.querySelector('.date-range-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = await this.fetchData(
                formData.get('start_date'),
                formData.get('end_date')
            );
            this.updateCharts(data);
        });
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsDashboard();
});
