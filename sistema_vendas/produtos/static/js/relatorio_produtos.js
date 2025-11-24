// Máscara para data DD/MM/AAAA
function mascaraData(input) {
    let valor = input.value.replace(/\D/g, '');
    
    if (valor.length <= 2) {
        input.value = valor;
    } else if (valor.length <= 4) {
        input.value = valor.slice(0, 2) + '/' + valor.slice(2);
    } else {
        input.value = valor.slice(0, 2) + '/' + valor.slice(2, 4) + '/' + valor.slice(4, 8);
    }
}

// Função para obter o CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Validar data
function validarData(data) {
    const regex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
    
    if (!regex.test(data)) {
        return false;
    }
    
    const partes = data.split('/');
    const dia = parseInt(partes[0], 10);
    const mes = parseInt(partes[1], 10);
    const ano = parseInt(partes[2], 10);
    
    if (ano < 1900 || ano > 2100) {
        return false;
    }
    
    if (mes < 1 || mes > 12) {
        return false;
    }
    
    const diasNoMes = new Date(ano, mes, 0).getDate();
    
    return dia >= 1 && dia <= diasNoMes;
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    const dataInicio = document.getElementById('dataInicio');
    const dataFinal = document.getElementById('dataFinal');
    const btnGerar = document.getElementById('btnGerarRelatorio');
    
    // Adicionar máscara aos inputs
    [dataInicio, dataFinal].forEach(input => {
        input.addEventListener('input', function() {
            mascaraData(this);
        });
        
        input.addEventListener('keypress', function(e) {
            if (!/\d/.test(e.key) && e.key !== 'Backspace' && e.key !== 'Delete') {
                e.preventDefault();
            }
        });
    });
    
    // Botão gerar relatório
    btnGerar.addEventListener('click', gerarRelatorio);
    
    // Menu toggle para mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Fechar sidebar ao clicar fora (mobile)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (sidebar && !sidebar.contains(e.target) && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        }
    });
});

// Gerar relatório
async function gerarRelatorio() {
    const dataInicio = document.getElementById('dataInicio').value;
    const dataFinal = document.getElementById('dataFinal').value;
    
    // Validações
    if (!dataInicio || !dataFinal) {
        alert('Por favor, preencha as datas de início e fim.');
        return;
    }
    
    if (!validarData(dataInicio) || !validarData(dataFinal)) {
        alert('Por favor, insira datas válidas no formato DD/MM/AAAA.');
        return;
    }
    
    // Mostrar loading
    mostrarLoading();
    
    try {
        const csrftoken = getCookie('csrftoken');
        
        const response = await fetch('/produtos/api/relatorio/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                dataInicio: dataInicio,
                dataFinal: dataFinal
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            exibirRelatorio(data.produtos, dataInicio, dataFinal);
        } else {
            alert('Erro: ' + (data.error || 'Erro ao gerar relatório'));
            mostrarEmptyState();
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao buscar dados do servidor');
        mostrarEmptyState();
    }
}

// Mostrar loading
function mostrarLoading() {
    const container = document.getElementById('reportContainer');
    container.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <p class="loading-text">Gerando relatório...</p>
        </div>
    `;
}

// Mostrar empty state
function mostrarEmptyState() {
    const container = document.getElementById('reportContainer');
    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <h3>Relatório Não Gerado</h3>
            <p>Selecione o período e clique em "Gerar Relatório" para visualizar os dados</p>
        </div>
    `;
}

// Exibir relatório
function exibirRelatorio(produtos, dataInicio, dataFinal) {
    const container = document.getElementById('reportContainer');
    
    if (!produtos || produtos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <h3>Nenhum Produto Vendido</h3>
                <p>Não foram encontradas vendas no período de ${dataInicio} até ${dataFinal}</p>
            </div>
        `;
        return;
    }
    
    // Encontrar o maior valor para calcular porcentagens
    const maxQuantidade = Math.max(...produtos.map(p => p.quantidade_vendida));
    
    // Montar HTML do relatório
    let html = `
        <div class="chart-container active">
            <div class="chart-header">
                <h3>Top ${produtos.length} Produtos Mais Vendidos</h3>
                <p>Período: ${dataInicio} até ${dataFinal}</p>
            </div>
            <div class="products-list">
    `;
    
    produtos.forEach((produto, index) => {
        const porcentagem = (produto.quantidade_vendida / maxQuantidade) * 100;
        
        html += `
            <div class="product-item">
                <div class="product-rank">${index + 1}º</div>
                <div class="product-info">
                    <div class="product-name">${produto.descricao}</div>
                    <div class="product-details">Código: ${produto.id}</div>
                </div>
                <div class="product-stats">
                    <div class="stat-item">
                        <div class="stat-label">Quantidade</div>
                        <div class="stat-value quantity">${produto.quantidade_vendida}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Faturamento</div>
                        <div class="stat-value">${produto.valor_total}</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-label">${porcentagem.toFixed(0)}% do líder</div>
                        <div class="progress-track">
                            <div class="progress-fill" style="width: ${porcentagem}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}