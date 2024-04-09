document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput_inactive');
    const customersTable = document.getElementById('customersTable_inactive');
    const tbody = customersTable.querySelector('tbody');

    searchInput.addEventListener('input', function () {
        const query = this.value;

        fetch('/search_customers_inactive', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${query}`
        })
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = '';

            data.forEach(client => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${client.name}</td>
                    <td>${client.address}</td>
                    <td>${client.phone}</td>
                    <td>${client.email}</td>
                    <td>${client.rnc}</td>
                    <td>
                        <a href="/active/${client.id}"><button id="edit">activar</button></a>
                    </td>`;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error:', error));
    });
});