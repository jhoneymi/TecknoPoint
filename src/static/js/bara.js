document.addEventListener("DOMContentLoaded", function() {
    // Hacemos una solicitud AJAX para obtener los datos del balance
    fetch('/CierreBalance_json')
        .then(response => response.json())
        .then(data => {
            // Datos del gráfico con los valores obtenidos del servidor
            var dataChart = {
                labels: ["Saldo Inicial", "Total Ingresos"],
                datasets: [{
                    label: 'saldo inicial', 
                    data: [data.saldo_inicial, data.total_ingresos],
                    backgroundColor: ["#CB4335", "#2ECC71"],
                    borderColor: ["#CB4335", "#2ECC71"]
                }]
            };

            // Opciones del gráfico
            var optionsChart = {
                responsive: true,
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            };

            // Crear el gráfico de barras
            var ctx = document.getElementById('myChart_bar').getContext('2d');
            var myChart = new Chart(ctx, {
                type: 'line',
                data: dataChart,
                options: optionsChart
            });
        })
        .catch(error => {
            console.error('Error al obtener los datos del balance:', error);
        });
});