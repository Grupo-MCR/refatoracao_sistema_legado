// Configuração da URL base da API
const API_BASE_URL = '/produtos/api';

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

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

async function loadProducts(searchTerm = '') {
    try {
        const url = searchTerm
            ? `${API_BASE_URL}/listar/?search=${encodeURIComponent(searchTerm)}`
            : `${API_BASE_URL}/listar/`;

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            renderProducts(data.produtos);
        } else {
            showError('Erro ao carregar produtos: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        showError('Erro ao conectar com o servidor');
    }
}

function renderProducts(products) {
    const container = document.getElementById('products-list');

    if (products.length === 0) {
        container.innerHTML = `
                    <div style="text-align: center; padding: 60px 20px; color: #808080;">
                        <p>Nenhum produto encontrado</p>
                    </div>
                `;
        return;
    }

    container.innerHTML = products.map(product => `
                <div class="product-card">
                    <div class="product-header">
                        <h3 class="product-title">${product.descricao}</h3>
                        <div class="product-actions">
                            <button class="icon-btn" onclick="editProduct(${product.id})" title="Editar">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                </svg>
                            </button>
                            <button class="icon-btn" onclick="deleteProduct(${product.id})" title="Excluir">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"/>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="product-details">
                        <div class="detail-item">
                            <span class="detail-label">Preço</span>
                            <span class="detail-value">${formatCurrency(product.preco)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Quantidade em Estoque</span>
                            <span class="detail-value">${product.qtd_estoque}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Fornecedor</span>
                            <span class="detail-value">${product.fornecedor.nome}</span>
                        </div>
                    </div>
                </div>
            `).join('');
}

function handleSearch(event) {
    if (event.key === 'Enter') {
        loadProductsWithSearch();
    }
}

function loadProductsWithSearch() {
    const searchTerm = document.getElementById('search-input').value;
    loadProducts(searchTerm);
}

async function deleteProduct(id) {
    if (!confirm('Tem certeza que deseja excluir este produto?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/deletar/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });

        const data = await response.json();

        if (data.success) {
            alert('Produto excluído com sucesso!');
            loadProducts();
        } else {
            alert('Erro ao excluir produto: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor');
    }
}

function editProduct(id) {
    window.location.href = `/produtos/cadastro/?id=${id}`;
}

function navigateToNew() {
    window.location.href = '/produtos/cadastro/';
}

function navigateTo(page) {
    console.log('Navegar para:', page);
    // Implementar navegação para outras páginas aqui
}

function showError(message) {
    const container = document.getElementById('products-list');
    container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: #ff6b35;">
                    <p>${message}</p>
                    <button class="btn" onclick="loadProducts()" style="margin-top: 20px;">Tentar Novamente</button>
                </div>
            `;
}

// Carregar produtos ao inicializar a página
window.onload = function () {
    loadProducts();
};