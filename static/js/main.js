// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effect to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.transition = 'transform 0.3s ease';
        });
    });

    // Add tooltips to icons
    const icons = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    icons.forEach(icon => {
        new bootstrap.Tooltip(icon);
    });

    // Add animation to numbers in stats cards
    const numbers = document.querySelectorAll('.display-4');
    numbers.forEach(number => {
        const finalValue = parseInt(number.textContent);
        let currentValue = 0;
        const duration = 1000; // 1 second
        const increment = finalValue / (duration / 16); // 60 FPS

        const animate = () => {
            currentValue = Math.min(currentValue + increment, finalValue);
            number.textContent = Math.floor(currentValue);
            
            if (currentValue < finalValue) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    });

    // Add fade-in effect to table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
    });

    // Initialize charts and predictions table if predictions data exists
    const predictionsElement = document.getElementById('predictions-data');
    if (predictionsElement) {
        try {
            const predictions = JSON.parse(predictionsElement.textContent);
            if (predictions && predictions.length > 0) {
                initializeCharts(predictions);
                populatePredictionsTable(predictions);
            } else {
                console.warn('No hay datos de predicción disponibles');
            }
        } catch (error) {
            console.error('Error al procesar los datos de predicción:', error);
        }
    }
});

function initializeCharts(predictions) {
    // Prepare data for trend chart
    const trendChartData = {
        labels: [],
        datasets: []
    };

    // Create a dataset for each product
    predictions.forEach((prediction, index) => {
        const colors = [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)'
        ];

        // Get dates for labels (use first product's dates)
        if (index === 0) {
            trendChartData.labels = prediction.predictions.map(p => 
                new Date(p.date).toLocaleDateString()
            );
        }

        // Add dataset for this product
        trendChartData.datasets.push({
            label: prediction.product.product_name,
            data: prediction.predictions.map(p => p.predicted_quantity),
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length].replace('0.7', '0.1'),
            tension: 0.4
        });
    });

    // Initialize trend chart
    const trendChart = new Chart(
        document.getElementById('stockTrendChart'),
        {
            type: 'line',
            data: trendChartData,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Tendencias de Stock por Producto'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cantidad'
                        }
                    }
                }
            }
        }
    );

    // Prepare data for status chart
    const statusData = {
        labels: ['Stock Normal', 'Stock Crítico', 'Sin Stock'],
        datasets: [{
            data: [
                predictions.filter(p => p.current_stock > p.threshold).length,
                predictions.filter(p => p.current_stock <= p.threshold && p.current_stock > 0).length,
                predictions.filter(p => p.current_stock === 0).length
            ],
            backgroundColor: [
                'rgba(75, 192, 192, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(255, 99, 132, 0.7)'
            ]
        }]
    };

    // Initialize status chart
    const statusChart = new Chart(
        document.getElementById('stockStatusChart'),
        {
            type: 'pie',
            data: statusData,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Estado del Stock'
                    }
                }
            }
        }
    );

    // Prepare data for comparison chart
    const comparisonData = {
        labels: predictions.map(p => p.product.product_name),
        datasets: [{
            label: 'Stock Actual',
            data: predictions.map(p => p.current_stock),
            backgroundColor: 'rgba(54, 162, 235, 0.7)',
        }, {
            label: 'Stock Mínimo',
            data: predictions.map(p => p.threshold),
            backgroundColor: 'rgba(255, 99, 132, 0.7)',
        }]
    };

    // Initialize comparison chart
    const comparisonChart = new Chart(
        document.getElementById('stockComparisonChart'),
        {
            type: 'bar',
            data: comparisonData,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Comparación Stock Actual vs. Mínimo'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cantidad'
                        }
                    }
                }
            }
        }
    );
}

function populatePredictionsTable(predictions) {
    const tbody = document.getElementById('predictions-table-body');
    if (!tbody) {
        console.warn('No se encontró la tabla de predicciones');
        return;
    }

    // Limpiar la tabla primero
    tbody.innerHTML = '';

    predictions.forEach(prediction => {
        try {
            // Obtener la última predicción (7 días)
            const lastPrediction = prediction.predictions[prediction.predictions.length - 1];
            
            // Calcular el cambio porcentual
            const currentStock = prediction.current_stock;
            const predictedStock = Math.round(lastPrediction.predicted_quantity);
            const percentChange = currentStock > 0 ? 
                ((predictedStock - currentStock) / currentStock * 100).toFixed(1) : 
                0;
            
            // Determinar la tendencia basada en el cambio porcentual
            let trend;
            if (Math.abs(percentChange) < 5) {
                trend = "Estable";
            } else if (percentChange > 0) {
                trend = "Alza";
            } else {
                trend = "Baja";
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${prediction.product.product_name}</td>
                <td class="text-center">${prediction.current_stock}</td>
                <td class="text-center">${prediction.threshold}</td>
                <td class="text-center">
                    ${predictedStock}
                    <small class="d-block text-muted">
                        (${percentChange > 0 ? '+' : ''}${percentChange}%)
                    </small>
                </td>
                <td class="text-center">
                    <span class="badge ${getTrendBadgeClass(trend)}">
                        ${formatTrend(trend)}
                    </span>
                </td>
            `;
            
            // Agregar clase de alerta si el stock predicho es menor al umbral
            if (predictedStock <= prediction.threshold) {
                tr.classList.add('table-warning');
            }
            
            tbody.appendChild(tr);
        } catch (error) {
            console.error('Error al procesar predicción:', error);
        }
    });

    // Aplicar animación de fade-in a las nuevas filas
    const newRows = tbody.querySelectorAll('tr');
    newRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
    });
}

function getTrendBadgeClass(trend) {
    switch(trend.toLowerCase()) {
        case 'alza':
            return 'bg-success';
        case 'baja':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

function formatTrend(trend) {
    switch(trend.toLowerCase()) {
        case 'alza':
            return '↑ Alza';
        case 'baja':
            return '↓ Baja';
        default:
            return '→ Estable';
    }
} 