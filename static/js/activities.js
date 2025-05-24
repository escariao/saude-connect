
async function listarAtividades() {
    const response = await fetch('/api/activities/');
    const atividades = await response.json();

    const lista = document.getElementById('lista-atividades');
    lista.innerHTML = '';

    atividades.forEach(act => {
        const item = document.createElement('li');
        item.textContent = `${act.activity_name} - ${act.description || ''} - R$${act.price || 'N/A'}`;
        lista.appendChild(item);
    });
}

async function criarAtividade(event) {
    event.preventDefault();
    const professional_id = document.getElementById('professional_id').value;
    const activity_name = document.getElementById('activity_name').value;
    const description = document.getElementById('description').value;
    const price = parseFloat(document.getElementById('price').value);
    const availability = document.getElementById('availability').value;

    await fetch('/api/activities/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ professional_id, activity_name, description, price, availability })
    });

    listarAtividades();
}
