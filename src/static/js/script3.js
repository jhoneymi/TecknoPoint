document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const employeesTable = document.getElementById('employeesTable');

    searchInput.addEventListener('input', function () {
        const query = this.value;

        fetch('/search_employees', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${query}`
        })
        .then(response => response.json())
        .then(data => {

            employeesTable.innerHTML = '';

            const headersRow = document.createElement('tr');
            headersRow.innerHTML = `
                <th>Fullname</th>
                <th>Email</th>
                <th>Username</th>
                <th>Password</th>
                <th>Operations</th>
            `;
            employeesTable.appendChild(headersRow);

            data.forEach(fila => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${fila[1]}</td>
                    <td>${fila[2]}</td>
                    <td>${fila[3]}</td>
                    <td>NULL</td>
                    <td>
                        <a href="/edit_emp/${fila[0]}"><button id="edit">Edit</button></a>
                        <a href="/remove_emp/${fila[0]}"><button id="remove" class="Borrar">Delete</button></a>
                    </td>
                `;
                employeesTable.appendChild(tr);
            });
        })
        .catch(error => console.error('Error:', error));
    });
});
