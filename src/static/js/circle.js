document.addEventListener("DOMContentLoaded", function() {
    // Hacemos una solicitud AJAX para obtener los datos del balance
    fetch('/CierreBalance_json')
        .then(response => response.json())
        .then(data => {
            // Datos del gráfico con los valores obtenidos del servidor
            var dataChart = {
                labels: ["Egresos", "Pago Efectivo", "Pago Tarjeta"],
                datasets: [{
                    data: [data.total_egresos, data.total_efectivo, data.total_tarjeta],
                    backgroundColor: ["#CB4335", "#2ECC71", "#2E86C1"],
                    hoverBackgroundColor: ["#CB4335", "#2ECC71", "#2E86C1"]
                }]
            };

            // Opciones del gráfico
            var optionsChart = {
                responsive: true,
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            var dataset = data.datasets[tooltipItem.datasetIndex];
                            var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
                                return previousValue + currentValue;
                            });
                            var currentValue = dataset.data[tooltipItem.index];
                            var percentage = ((currentValue / total) * 100).toFixed(2);
                            return percentage + "%";
                        }
                    }
                }
            };

            // Crear el gráfico circular
            var ctx = document.getElementById('myChart').getContext('2d');
            var myChart = new Chart(ctx, {
                type: 'doughnut',
                data: dataChart,
                options: optionsChart
            });
        })
        .catch(error => {
            console.error('Error al obtener los datos del balance:', error);
        });
});