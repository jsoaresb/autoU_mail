document.getElementById('emailForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const resultsSection = document.getElementById('results-section');
    const loading = document.getElementById('loading');
    const resultBox = document.getElementById('result-box');

    // Mostra a seção de resultados com o spinner
    resultsSection.classList.remove('hidden');
    resultsSection.classList.remove('fade-in-animation');
    loading.style.display = 'block';
    resultBox.style.display = 'none';

    // Cria um FormData para enviar o texto ou arquivo
    const formData = new FormData();
    const emailText = document.getElementById('email_text').value;
    const emailFile = document.getElementById('email_file').files[0];

    if (emailText) {
        formData.append('email_text', emailText);
    } else if (emailFile) {
        formData.append('email_file', emailFile);
    } else {
        alert("Por favor, cole um texto ou faça o upload de um arquivo.");
        loading.style.display = 'none';
        return;
    }

    try {
        const response = await fetch('/processar', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (response.ok) {
            document.getElementById('categoria_resultado').textContent = result.categoria;
            document.getElementById('resposta_sugerida').textContent = result.resposta;
            
            // Esconde o spinner e mostra os resultados
            loading.style.display = 'none';
            resultBox.style.display = 'block';
            resultsSection.classList.add('fade-in-animation');
        } else {
            alert('Erro: ' + result.error);
            loading.style.display = 'none';
        }
    } catch (error) {
        alert('Ocorreu um erro ao se conectar com o servidor.');
        loading.style.display = 'none';
    }
});
