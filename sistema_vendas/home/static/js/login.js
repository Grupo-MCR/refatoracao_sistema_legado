let URL_LOGIN = "http://127.0.0.1:8000/login/";

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

async function realizarLogin(event) {
    event.preventDefault();

    let from = document.getElementById("formLogin");
    let fd = new FormData();
    from.querySelectorAll(".formInput").forEach(element => {
        fd.append(element.name, element.value);
    })

    console.log(fd);
    console.log(Array.from(fd));

    const body = new URLSearchParams(fd);
    console.log(body);

    fetch(URL_LOGIN, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin', 
        body: body,
    })
    .then(response => {
        if(!response.ok) {
            return response.text().then(text => {
                throw new Error(text);
            });
        }
        if(response.redirected) {
            window.location.replace(response.url);
        }
        return response.text();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.log(error);
    })
}