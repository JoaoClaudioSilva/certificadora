function flashElemento(cor, botao) {
    setTimeout(function () {
        botao.style.backgroundColor = cor;
    }, 0);

    setTimeout(function () {
        botao.removeAttribute('style');
    }, 1000);
}

function opcaoEscolhida(botaoAcionado){

    const xhr = new XMLHttpRequest();

    xhr.open("GET", "/questao/endpoint/" + "?opcao=" + botaoAcionado.id);
    xhr.send();

    xhr.responseType = "text";
    xhr.onload = () => {
        if (xhr.readyState === 4 && xhr.status === 200) {
            resposta = xhr.response;
            if(resposta == 1) flashElemento('blue', botaoAcionado);
            if(resposta == 0) flashElemento('red', botaoAcionado);
        } else {
            console.log(`Error: ${xhr.status}`);
        }
    };
}


function destruirPopup(){
    let overlay = document.getElementById('overlay');
    let popup = document.getElementById('popup');

    if(overlay && popup){
        overlay.remove();
        popup.remove();
    }
}

