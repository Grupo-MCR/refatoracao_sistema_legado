const URL = window.location.href;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function conferirSenha() {
    senha = document.getElementById("senhaFuncionarioInput");
    senhaMirror = document.getElementById("senhaValidationFuncionarioInput");
    if(senha.value != senhaMirror.value) {
        return false;
    }
    return true;
}

async function mandarFuncionario(event) {
    event.preventDefault();

    if(!conferirSenha()) {
        alert("erro: as senhas não são identicas");
        return;
    }

    let fields = document.querySelectorAll(".funcionarioInput");
    let hopes = document.querySelectorAll(".funcionarioSelect");
    let dreams = new FormData();

    fields.forEach((field) => {
        dreams.append(field.name, field.value);
    })

    hopes.forEach((select) => {
        dreams.append(select.name, select.value);
    })

    let fieldsOfHopesAndDreams = Array.from(dreams);
    console.log(fieldsOfHopesAndDreams);

    const body = new URLSearchParams(dreams);

    fetch(URL, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: body, 
    })
    .then((response) => {
        if(!response.ok) {
            return response.text().then((text) => {
                throw new Error(text);
            });
        }
        if(response.redirected) {
            window.location.replace(response.url);
        }
        return response.text();
    })
    .then((data) => {
        console.log(data);
    })
    .catch((error) => {
        console.log(error);
        alert(error);
    })
}