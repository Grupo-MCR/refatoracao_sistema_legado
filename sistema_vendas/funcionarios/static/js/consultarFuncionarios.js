const URL = "http://127.0.0.1:8000/funcionarios/api/buscarFuncionarios";

window.addEventListener("load", async () => {
    const divCards = document.querySelector("#cardsDiv");

    try {
        fetch(URL, {
            method: 'GET',
        })
        .then((response) => {
            if(!response.ok) {
                response.text().then((text) => {
                    throw new Error(text)
                });
            }
            return response.json();
        })
        .then((data) => {
            console.log(data);
                
            if(data && data.length) {
                data.forEach(element => {
                    let card = buildCard(element);
                    divCards.appendChild(card);
                });
            } else {
                console.log("nenhum dado encontrado no sistema");
            }
        })
        .catch((error) => {
            console.log(error);
        })
    
    } catch(e) {
        console.log("erro ao buscar dados do sistema :p");
    }
})

function buildCard(data) {
    //titulo 
    let titulo = document.createElement('h3');
    titulo.classList.add("funcionarioCardNome");
    titulo.innerText = data['nome'];

    //cpf
    let tituloCpf = document.createElement('h4');
    tituloCpf.innerText = "CPF";

    let textCpf = document.createElement('i');
    textCpf.innerText = data['cpf'];

    let divCpf = document.createElement('div');
    divCpf.classList.add("funcionarioCardCpf");
    divCpf.appendChild(tituloCpf);
    divCpf.appendChild(textCpf);

    //cargo
    let tituloCargo = document.createElement('h4');
    tituloCargo.innerText = "Cargo";

    let textCargo = document.createElement('i');
    textCargo.innerText = data['cargo'];

    let divCargo = document.createElement('div');
    divCargo.classList.add("funcionarioCardCargo");
    divCargo.appendChild(tituloCargo);
    divCargo.appendChild(textCargo);

    //email
    let tituloEmail = document.createElement('h4');
    tituloEmail.innerText = "Email";

    let textEmail = document.createElement('i');
    textEmail.innerText = data['email'];

    let divEmail = document.createElement('div');
    divEmail.classList.add("funcionarioCardEmail");
    divEmail.appendChild(tituloEmail);
    divEmail.appendChild(textEmail);

    //endereço
    let tituloEndereco = document.createElement('h4');
    tituloEndereco.innerText = "Endereço";

    let textEndereco = document.createElement('i');
    textEndereco.innerText = data['cidade'] + " - " + data['estado'];

    let divEndereco = document.createElement('div');
    divEndereco.classList.add("funcionarioCardEndereco");
    divEndereco.appendChild(tituloEndereco);
    divEndereco.appendChild(textEndereco);

    //botões

    //editar
    let iconEditar = document.createElement('i');
    iconEditar.classList.add("fa-solid");
    iconEditar.classList.add("fa-pen-to-square");
    iconEditar.classList.add("cardButton");

    let botaoEditar = document.createElement('a');
    botaoEditar.href = "http://127.0.0.1:8000/funcionarios/editar/id=" + data['id'];
    botaoEditar.appendChild(iconEditar);

    //deletar
    let iconDeletar = document.createElement('i');
    iconDeletar.classList.add("fa-solid")
    iconDeletar.classList.add("fa-trash-can");
    iconDeletar.classList.add("cardButton");

    let botaoDeletar = document.createElement('a');
    botaoDeletar.classList.add("botaoDeletar");
    botaoDeletar.href = "deletar_funcionario";
    botaoDeletar.onclick = function() {deletarFuncionario(event, data['id'])};
    botaoDeletar.appendChild(iconDeletar);

    let divBotoes = document.createElement('div');
    divBotoes.classList.add("funcionarioCardEditButton");
    divBotoes.appendChild(botaoEditar);
    divBotoes.appendChild(botaoDeletar);

    //card funcionario
    let divCard = document.createElement('div');
    divCard.classList.add("funcionarioCard");
    divCard.appendChild(titulo);
    divCard.appendChild(divCpf);
    divCard.appendChild(divCargo);
    divCard.appendChild(divEmail);
    divCard.appendChild(divEndereco);
    divCard.appendChild(divBotoes);

    return divCard;
}

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


function deletarFuncionario(event, id) {
    event.preventDefault();
    let URL_DELETAR = "http://127.0.0.1:8000/funcionarios/api/apagarFuncionario/id=" + id;
    try {
        fetch(URL_DELETAR, {
            method: 'DELETE',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin',
        })
        .then((response) => {
            if(!response.ok) {
                response.text().then((text) => {
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
            alert(data);
        })
        .catch((error) => {
            console.log(error);
            throw new Error(error);
        })
    } catch(error) {
        console.log(error);
        alert(error);
    }
}