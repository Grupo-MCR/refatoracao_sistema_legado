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

// Aplicar máscara aos campos de data
document.addEventListener('DOMContentLoaded', function() {
    const dataInicio = document.getElementById('dataInicio');
    const dataFim = document.getElementById('dataFim');
    const dataVenda = document.getElementById('dataVenda');
    
    // Adicionar máscara aos inputs de data
    [dataInicio, dataFim, dataVenda].forEach(input => {
        input.addEventListener('input', function() {
            mascaraData(this);
        });
        
        input.addEventListener('keypress', function(e) {
            if (!/\d/.test(e.key) && e.key !== 'Backspace' && e.key !== 'Delete') {
                e.preventDefault();
            }
        });
    });
    
    // Botão de pesquisa do histórico de vendas
    const btnPesquisarHistorico = document.querySelector('.sales-history .btn-search');
    btnPesquisarHistorico.addEventListener('click', function() {
        pesquisarHistorico();
    });
    
    // Botão de pesquisa do total de vendas
    const btnPesquisarTotal = document.querySelector('.sales-total .btn-search');
    btnPesquisarTotal.addEventListener('click', function() {
        pesquisarTotal();
    });
    
    // Menu toggle para mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    menuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });
    
    // Fechar sidebar ao clicar fora (mobile)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        }
    });
});

// Função para pesquisar histórico de vendas
function pesquisarHistorico() {
    const dataInicio = document.getElementById('dataInicio').value;
    const dataFim = document.getElementById('dataFim').value;
    
    // Validação básica
    if (!dataInicio || !dataFim) {
        alert('Por favor, preencha as datas de início e fim.');
        return;
    }
    
    if (!validarData(dataInicio) || !validarData(dataFim)) {
        alert('Por favor, insira datas válidas no formato DD/MM/AAAA.');
        return;
    }
    
    // Aqui você fará a chamada para o backend
    console.log('Pesquisando vendas de', dataInicio, 'até', dataFim);
    
    // Exemplo de como preencher a tabela (simulação)
    exibirResultadosHistorico([
        {
            codigo: '001',
            data: '15/11/2024',
            cliente: 'João Silva',
            total: 'R$ 150,00',
            obs: 'Pagamento à vista'
        },
        {
            codigo: '002',
            data: '16/11/2024',
            cliente: 'Maria Santos',
            total: 'R$ 320,50',
            obs: 'Parcelado 3x'
        }
    ]);
}

// Função para pesquisar total de vendas por data
function pesquisarTotal() {
    const dataVenda = document.getElementById('dataVenda').value;
    
    // Validação básica
    if (!dataVenda) {
        alert('Por favor, preencha a data da venda.');
        return;
    }
    
    if (!validarData(dataVenda)) {
        alert('Por favor, insira uma data válida no formato DD/MM/AAAA.');
        return;
    }
    
    // Aqui você fará a chamada para o backend
    console.log('Pesquisando total de vendas em', dataVenda);
    
    // Exemplo de como exibir o resultado (simulação)
    exibirTotal('R$ 1.850,75');
}

// Função para validar data no formato DD/MM/AAAA
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

// Função para exibir resultados do histórico na tabela
function exibirResultadosHistorico(vendas) {
    const tbody = document.getElementById('salesTableBody');
    tbody.innerHTML = '';
    
    if (vendas.length === 0) {
        tbody.innerHTML = '<tr class="empty-state"><td colspan="5">Nenhuma venda encontrada no período selecionado</td></tr>';
        return;
    }
    
    vendas.forEach(venda => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${venda.codigo}</td>
            <td>${venda.data}</td>
            <td>${venda.cliente}</td>
            <td>${venda.total}</td>
            <td>${venda.obs}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Função para exibir o total de vendas
function exibirTotal(total) {
    const resultBox = document.querySelector('.result-box');
    resultBox.innerHTML = `<p class="total-value">${total}</p>`;
}

// Funções auxiliares para integração com backend (exemplos)

// Exemplo de função para fazer requisição ao backend
async function buscarVendasPorPeriodo(dataInicio, dataFim) {
    try {
        const response = await fetch('/api/vendas/periodo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dataInicio: dataInicio,
                dataFim: dataFim
            })
        });
        
        if (!response.ok) {
            throw new Error('Erro ao buscar vendas');
        }
        
        const dados = await response.json();
        return dados;
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao buscar dados do servidor');
        return [];
    }
}

// Exemplo de função para buscar total por data
async function buscarTotalPorData(data) {
    try {
        const response = await fetch('/api/vendas/total', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: data
            })
        });
        
        if (!response.ok) {
            throw new Error('Erro ao buscar total');
        }
        
        const dados = await response.json();
        return dados.total;
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao buscar dados do servidor');
        return null;
    }
}
