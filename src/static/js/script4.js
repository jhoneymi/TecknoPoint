document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const suppliersTable = document.getElementById('suppliersTable');
    const tbody = suppliersTable.querySelector('tbody');

    searchInput.addEventListener('input', function () {
        const query = this.value;

        fetch('/search_suppliers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${query}`
        })
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = '';

            data.forEach(prov => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${prov.name}</td>
                    <td>${prov.address}</td>
                    <td>${prov.phone}</td>
                    <td>${prov.email}</td>
                    <td>
                        <a href="/edit_prov/${prov.id}"><button id="edit">Edit</button></a>
                        <a href="/remove_prov/${prov.id}"><button id="remove" class="Borrar">Delete</button></a>
                    </td>`;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error:', error));
    });
});
