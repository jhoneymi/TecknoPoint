document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const customersTable = document.getElementById('customersTable');
    const tbody = customersTable.querySelector('tbody');

    searchInput.addEventListener('input', function () {
        const query = this.value;

        fetch('/search_customers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${query}`
        })
        .then(response => response.json())
        .then(data => {
            // Limpiar resultados anteriores
            tbody.innerHTML = '';

            // Mostrar resultados
            data.forEach(client => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${client.name}</td>
                    <td>${client.address}</td>
                    <td>${client.phone}</td>
                    <td>${client.email}</td>
                    <td>${client.rnc}</td>
                    <td>
                        <a href="/edit_customer/${client.id}"><button id="edit">Edit</button></a>
                        <a href="/deactivate_client/${client.id}"><button id="remove" class="Borrar">Delete</button></a>
                    </td>`;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error:', error));
    });
});