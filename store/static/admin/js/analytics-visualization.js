class AnalyticsVisualizer {
    constructor() {
        this.heatmapInstance = this.initializeHeatmap();
        this.bindEvents();
    }

    initializeHeatmap() {
        return h337.create({
            container: document.getElementById('heatmapContainer'),
            radius: 25,
            maxOpacity: .6,
            minOpacity: 0,
            blur: .75
        });
    }

    bindEvents() {
        document.getElementById('generateHeatmap').addEventListener('click', () => {
            this.generateHeatmap();
        });

        document.getElementById('pageSelector').addEventListener('change', () => {
            this.updateMetrics();
        });

        document.getElementById('deviceType').addEventListener('change', () => {
            this.updateMetrics();
        });
    }

    async generateHeatmap() {
        const page = document.getElementById('pageSelector').value;
        const device = document.getElementById('deviceType').value;
        
        try {
            const response = await fetch(`/api/analytics/heatmap-data/?page=${page}&device=${device}`);
            const data = await response.json();
            
            this.heatmapInstance.setData({
                max: data.max,
                data: this.transformClickData(data.clicks)
            });
            
            this.updateMetrics(data.metrics);
        } catch (error) {
            console.error('Error generating heatmap:', error);
        }
    }

    transformClickData(clicks) {
        return clicks.map(click => ({
            x: click.x,
            y: click.y,
            value: click.count
        }));
    }

    updateMetrics(metrics) {
        if (metrics) {
            document.getElementById('totalClicks').textContent = metrics.total_clicks;
            document.getElementById('hotAreas').textContent = metrics.hot_areas;
        }
    }
}

// Initialize visualizer
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsVisualizer();
});
