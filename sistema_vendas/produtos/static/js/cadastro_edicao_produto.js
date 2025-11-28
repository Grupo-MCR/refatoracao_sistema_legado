// Configuração da URL base da API
const API_BASE_URL = '/produtos/api';

let isEditMode = false;
let currentProductId = null;

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

const csrftoken = getCookie('csrftoken');

// Carregar fornecedores do backend
async function loadFornecedores() {
    try {
        const response = await fetch(`${API_BASE_URL}/fornecedores/`);
        const data = await response.json();

        if (data.success) {
            const select = document.getElementById('fornecedor');
            // Limpa opções existentes (exceto a primeira)
            select.innerHTML = '<option value="">Selecione um fornecedor</option>';

            data.fornecedores.forEach(fornecedor => {
                const option = document.createElement('option');
                option.value = fornecedor.id;
                option.textContent = `${fornecedor.nome} - ${fornecedor.cnpj}`;
                select.appendChild(option);
            });
        } else {
            alert('Erro ao carregar fornecedores: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor');
    }
}

// Formatar preço enquanto digita
function formatPrice(input) {
    let value = input.value.replace(/\D/g, '');
    if (value === '') {
        input.value = '';
        return;
    }
    value = (parseInt(value) / 100).toFixed(2);
    value = value.replace('.', ',');
    value = value.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
    input.value = 'R$ ' + value;
}

// Converter preço formatado para número
function parsePrice(priceString) {
    if (!priceString) return 0;
    return parseFloat(priceString.replace('R$', '').replace(/\./g, '').replace(',', '.').trim());
}

// Formatar valor numérico para exibição no input
function formatCurrencyForInput(value) {
    let formatted = value.toFixed(2).replace('.', ',');
    formatted = formatted.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
    return 'R$ ' + formatted;
}

// Carregar dados do produto para edição
async function loadProductData(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/obter/${productId}/`);
        const data = await response.json();

        if (data.success) {
            const product = data.produto;
            
            isEditMode = true;
            currentProductId = product.id;

            document.getElementById('form-title').textContent = 'Editar Produto';
            document.getElementById('submit-btn').textContent = 'Salvar Alterações';
            document.getElementById('product-id').value = product.id;
            document.getElementById('descricao').value = product.descricao;
            document.getElementById('preco').value = formatCurrencyForInput(product.preco);
            document.getElementById('qtd-estoque').value = product.qtd_estoque;
            document.getElementById('fornecedor').value = product.fornecedor.id;
        } else {
            alert('Erro ao carregar produto: ' + data.error);
            goBack();
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor');
        goBack();
    }
}

// Enviar formulário (criar ou atualizar)
async function submitProduct(e) {
    e.preventDefault();

    const formData = {
        descricao: document.getElementById('descricao').value,
        preco: parsePrice(document.getElementById('preco').value),
        qtd_estoque: parseInt(document.getElementById('qtd-estoque').value),
        fornecedor: parseInt(document.getElementById('fornecedor').value)
    };

    // Validações básicas
    if (!formData.descricao) {
        alert('Por favor, preencha a descrição do produto');
        return;
    }

    if (formData.preco <= 0) {
        alert('Por favor, informe um preço válido');
        return;
    }

    if (formData.qtd_estoque < 0) {
        alert('A quantidade em estoque não pode ser negativa');
        return;
    }

    if (!formData.fornecedor) {
        alert('Por favor, selecione um fornecedor');
        return;
    }

    try {
        let response;
        
        if (isEditMode) {
            // Atualizar produto existente
            response = await fetch(`${API_BASE_URL}/atualizar/${currentProductId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(formData)
            });
        } else {
            // Criar novo produto
            response = await fetch(`${API_BASE_URL}/criar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(formData)
            });
        }

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            // Redirecionar DIRETAMENTE para a URL correta
            window.location.href = '/produtos/consulta_produto/';
        } else {
            alert('Erro: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor');
    }
}

// Voltar para página de consulta
function goBack() {
    // URL CORRETA com underscore
    window.location.href = '/produtos/consulta_produto/';
}

// Navegação do menu
function navigateTo(page) {
    const routes = {
        'vendas': '/ponto_venda/',
        'pagamentos': '/pagamentos/',
        'produtos': '/produtos/consulta_produto/',
        'clientes': '/clientes/consulta_cliente/',
        'fornecedores': '/fornecedores/consultar/',
        'funcionarios': '/funcionarios/consultar/',
        'vendas-list': '/historico_vendas/',
        'relatorio': '/produtos/relatorio/'
    };

    if (routes[page]) {
        window.location.href = routes[page];
    } else {
        console.log('Rota não implementada:', page);
    }
}

// Inicializar página
window.onload = async function () {

    // força remoção de parâmetros restaurados pelo navegador
    if (performance.getEntriesByType("navigation")[0].type === "back_forward") {
        history.replaceState({}, '', window.location.pathname);
    }

    await loadFornecedores();

    const productId = (new URL(window.location.href)).searchParams.get('id');

    if (productId) {
        await loadProductData(productId);
    }
};

