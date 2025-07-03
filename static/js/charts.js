// Chart.js configurations and utilities

// Default chart options
const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
        },
        tooltip: {
            mode: 'index',
            intersect: false,
        }
    },
    scales: {
        x: {
            display: true,
            title: {
                display: true
            }
        },
        y: {
            display: true,
            title: {
                display: true
            },
            beginAtZero: true
        }
    }
};

// Color palette for charts
const chartColors = {
    primary: 'rgba(13, 110, 253, 0.8)',
    secondary: 'rgba(108, 117, 125, 0.8)',
    success: 'rgba(25, 135, 84, 0.8)',
    danger: 'rgba(220, 53, 69, 0.8)',
    warning: 'rgba(255, 193, 7, 0.8)',
    info: 'rgba(13, 202, 240, 0.8)',
    light: 'rgba(248, 249, 250, 0.8)',
    dark: 'rgba(33, 37, 41, 0.8)'
};

// Create line chart
function createLineChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chartOptions = { ...defaultChartOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: chartOptions
    });
}

// Create bar chart
function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chartOptions = { ...defaultChartOptions, ...options };
    
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: chartOptions
    });
}

// Create pie chart
function createPieChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        },
        ...options
    };
    
    return new Chart(ctx, {
        type: 'pie',
        data: data,
        options: chartOptions
    });
}

// Create doughnut chart
function createDoughnutChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        return `${label}: $${value.toFixed(2)}`;
                    }
                }
            }
        },
        ...options
    };
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: chartOptions
    });
}

// Format currency for chart labels
function formatCurrencyForChart(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Generate random colors for charts
function generateChartColors(count) {
    const colors = [];
    const baseColors = Object.values(chartColors);
    
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    
    return colors;
}

// Create sales trend chart
function createSalesTrendChart(canvasId, salesData) {
    const data = {
        labels: salesData.map(item => item.date),
        datasets: [{
            label: 'Sales ($)',
            data: salesData.map(item => item.sales),
            borderColor: chartColors.primary,
            backgroundColor: chartColors.primary.replace('0.8', '0.1'),
            fill: true,
            tension: 0.4
        }]
    };
    
    const options = {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrencyForChart(value);
                    }
                }
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `Sales: ${formatCurrencyForChart(context.parsed.y)}`;
                    }
                }
            }
        }
    };
    
    return createLineChart(canvasId, data, options);
}

// Create inventory status chart
function createInventoryStatusChart(canvasId, inventoryData) {
    const data = {
        labels: ['In Stock', 'Low Stock', 'Out of Stock'],
        datasets: [{
            data: [
                inventoryData.inStock,
                inventoryData.lowStock,
                inventoryData.outOfStock
            ],
            backgroundColor: [
                chartColors.success,
                chartColors.warning,
                chartColors.danger
            ],
            borderWidth: 0
        }]
    };
    
    return createPieChart(canvasId, data);
}

// Create top products chart
function createTopProductsChart(canvasId, productsData) {
    const data = {
        labels: productsData.map(item => item.name),
        datasets: [{
            label: 'Quantity Sold',
            data: productsData.map(item => item.quantity),
            backgroundColor: generateChartColors(productsData.length),
            borderWidth: 1
        }]
    };
    
    const options = {
        indexAxis: 'y',
        scales: {
            x: {
                beginAtZero: true
            }
        }
    };
    
    return createBarChart(canvasId, data, options);
}

// Initialize charts when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Chart.js global configuration
    Chart.defaults.font.family = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#6c757d';
    Chart.defaults.borderColor = '#dee2e6';
    Chart.defaults.backgroundColor = 'rgba(0, 0, 0, 0.1)';
});
