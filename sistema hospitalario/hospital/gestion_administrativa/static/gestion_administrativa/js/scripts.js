// Mensaje de alerta para botones
document.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', () => {
        alert(`Has hecho clic en "${btn.textContent}"`);
    });
});

// Inicialización de gráficos (si existieran en tu HTML)
document.addEventListener('DOMContentLoaded', () => {
    const ingresosCanvas = document.getElementById('ingresosChart');
    const desempenoCanvas = document.getElementById('desempenoChart');

    if (ingresosCanvas) {
        const datos = JSON.parse(document.getElementById('datos-ingresos-json').textContent);
        const labels = datos.map(d => d.mes);
        const montos = datos.map(d => d.monto);
        new Chart(ingresosCanvas.getContext('2d'), {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Ingresos (USD)',
                    data: montos,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } },
                plugins: { legend: { display: false } }
            }
        });
    }

    if (desempenoCanvas) {
        const datos = JSON.parse(document.getElementById('datos-desempeno-json').textContent);
        const labels = datos.map(d => d.doctor);
        const citas = datos.map(d => d.citas_atendidas);
        new Chart(desempenoCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Citas Atendidas',
                    data: citas,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(255, 206, 86, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                scales: { x: { beginAtZero: true } },
                plugins: { legend: { display: false } }
            }
        });
    }
});
