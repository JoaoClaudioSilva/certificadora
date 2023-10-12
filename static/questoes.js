const botaoFiltro = document.getElementById('botao_filtro');
const opcoesFiltro = document.getElementById('opcoes_filtro');


botaoFiltro.addEventListener('click', function () {
    if (opcoesFiltro.style.display === 'flex') {
        opcoesFiltro.style.display = 'none';
    } else {
        opcoesFiltro.style.display = 'flex';
    }
});


const botaoAsc = document.getElementById('botao_asc');
const botaoDesc = document.getElementById('botao_desc');


botaoAsc.addEventListener('click', function() {

    const url = window.location.href;
    const novaUrl = url.replace(/\?.*$/, '') + '?ord=asc';
    window.location.href = novaUrl;
});

botaoDesc.addEventListener('click', function() {

    const url = window.location.href;
    const novaUrl = url.replace(/\?.*$/, '') + '?ord=desc';
    window.location.href = novaUrl;
});
