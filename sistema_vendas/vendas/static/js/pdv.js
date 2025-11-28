document.addEventListener('DOMContentLoaded', () => {
  // Elementos do formulário - Cliente
  const cpfInput = document.querySelector('input[placeholder="000.000.000-00"]');
  const btnBuscarCliente = cpfInput.nextElementSibling;
  const nomeInput = document.querySelector('input[placeholder="Pesquise o cliente pelo CPF"]');
  const dataInput = document.querySelector('input[type="date"]');
  
  // Elementos do formulário - Produto
  const codInput = document.querySelector('input[placeholder="000"]');
  const btnBuscarProduto = codInput.nextElementSibling;
  const prodInput = document.querySelector('input[placeholder="Pesquise pelo código"]');
  const precoInput = document.querySelector('input[placeholder="0,00"]');
  const qtdInput = document.querySelector('input[type="number"]');
  const btnAdicionar = document.querySelector('.fa-plus').parentElement;
  
  // Elementos da tabela e totais
  const tabela = document.querySelector('tbody');
  const totalSpan = document.querySelector('.total-box span');
  const btnPagamento = document.querySelector('.btn-orange');
  const btnCancelar = document.querySelector('.btn-cancel');
  
  // Estado da aplicação
  let itens = [];
  let total = 0;
  let clienteId = null;
  let estoqueAtual = {};
  
  // Configurar data atual
  const hoje = new Date().toISOString().split('T')[0];
  dataInput.value = hoje;
  
  // ========== FUNÇÕES AUXILIARES ==========
  
  // Obter CSRF token
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
  
  // Formatar valor para moeda brasileira
  function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    });
  }
  
  // Converter string para número
  function stringParaNumero(str) {
    if (!str) return 0;
    return parseFloat(str.toString().replace(/\./g, '').replace(',', '.')) || 0;
  }
  
  // Exibir notificação
  function mostrarNotificacao(mensagem, tipo = 'info') {
    const cores = {
      'sucesso': '#4CAF50',
      'erro': '#f44336',
      'aviso': '#ff9800',
      'info': '#2196F3'
    };
    
    const notif = document.createElement('div');
    notif.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${cores[tipo] || cores.info};
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      z-index: 9999;
      animation: slideIn 0.3s ease-out;
      max-width: 350px;
      font-size: 14px;
    `;
    notif.textContent = mensagem;
    
    document.body.appendChild(notif);
    
    setTimeout(() => {
      notif.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => notif.remove(), 300);
    }, 3000);
  }
  
  // Adicionar animações CSS
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(400px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(400px); opacity: 0; }
    }
    .destaque-linha {
      animation: destacar 0.5s ease-out;
    }
    @keyframes destacar {
      0%, 100% { background-color: transparent; }
      50% { background-color: rgba(255, 102, 0, 0.2); }
    }
    .btn-remover {
      background: #f44336;
      color: white;
      border: none;
      padding: 5px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
    }
    .btn-remover:hover {
      background: #d32f2f;
    }
  `;
  document.head.appendChild(style);
  
  // ========== MÁSCARAS ==========
  
  // Máscara para CPF
  cpfInput.addEventListener('input', (e) => {
    let valor = e.target.value.replace(/\D/g, '');
    if (valor.length <= 11) {
      valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
      valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
      valor = valor.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      e.target.value = valor;
    }
  });
  
  // Máscara para preço
  precoInput.addEventListener('input', (e) => {
    let valor = e.target.value.replace(/\D/g, '');
    if (valor === '') {
      e.target.value = '0,00';
      return;
    }
    valor = (parseInt(valor) / 100).toFixed(2);
    e.target.value = formatarMoeda(parseFloat(valor));
  });
  
  // ========== BUSCAR CLIENTE ==========
  
  async function buscarCliente() {
    const cpf = cpfInput.value.trim();
    
    if (!cpf || cpf.length < 14) {
      mostrarNotificacao('Digite um CPF válido', 'aviso');
      cpfInput.focus();
      return;
    }
    
    btnBuscarCliente.disabled = true;
    btnBuscarCliente.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    
    try {
      const response = await fetch(`/venda/buscar_cliente/?cpf=${encodeURIComponent(cpf)}`);
      const data = await response.json();
      
      if (response.ok && data.nome) {
        nomeInput.value = data.nome;
        clienteId = data.id;
        mostrarNotificacao(`Cliente encontrado: ${data.nome}`, 'sucesso');
        
        // Destaca o campo nome
        nomeInput.style.borderColor = '#4CAF50';
        setTimeout(() => { nomeInput.style.borderColor = '#333'; }, 2000);
      } else {
        nomeInput.value = '';
        clienteId = null;
        mostrarNotificacao(data.erro || 'Cliente não encontrado', 'aviso');
      }
    } catch (error) {
      console.error('Erro ao buscar cliente:', error);
      mostrarNotificacao('Erro ao buscar cliente', 'erro');
    } finally {
      btnBuscarCliente.disabled = false;
      btnBuscarCliente.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i>';
    }
  }
  
  btnBuscarCliente.addEventListener('click', buscarCliente);
  
  cpfInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      buscarCliente();
    }
  });
  
  // ========== BUSCAR PRODUTO ==========
  
  async function buscarProduto() {
    const codigo = codInput.value.trim();
    
    if (!codigo) {
      mostrarNotificacao('Digite um código para buscar', 'aviso');
      codInput.focus();
      return;
    }
    
    btnBuscarProduto.disabled = true;
    btnBuscarProduto.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    
    try {
      const response = await fetch(`/venda/buscar_produto/?codigo=${encodeURIComponent(codigo)}`);
      const data = await response.json();
      
      if (response.ok && data.descricao) {
        prodInput.value = data.descricao;
        precoInput.value = formatarMoeda(data.preco);
        qtdInput.value = 1;
        qtdInput.max = data.qtd_estoque;
        estoqueAtual[codigo] = data.qtd_estoque;
        
        if (data.qtd_estoque === 0) {
          mostrarNotificacao('⚠️ Produto sem estoque!', 'aviso');
          qtdInput.value = 0;
          qtdInput.disabled = true;
        } else {
          qtdInput.disabled = false;
          mostrarNotificacao(`Produto: ${data.descricao} (Estoque: ${data.qtd_estoque})`, 'sucesso');
          qtdInput.focus();
          qtdInput.select();
        }
        
        // Destaca campos preenchidos
        prodInput.style.borderColor = '#4CAF50';
        precoInput.style.borderColor = '#4CAF50';
        setTimeout(() => {
          prodInput.style.borderColor = '#333';
          precoInput.style.borderColor = '#333';
        }, 2000);
      } else {
        limparCamposProduto();
        mostrarNotificacao(data.erro || 'Produto não encontrado', 'aviso');
      }
    } catch (error) {
      console.error('Erro ao buscar produto:', error);
      mostrarNotificacao('Erro ao buscar produto', 'erro');
      limparCamposProduto();
    } finally {
      btnBuscarProduto.disabled = false;
      btnBuscarProduto.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i>';
    }
  }
  
  function limparCamposProduto() {
    prodInput.value = '';
    precoInput.value = '0,00';
    qtdInput.value = 0;
    qtdInput.disabled = false;
  }
  
  btnBuscarProduto.addEventListener('click', buscarProduto);
  
  codInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      buscarProduto();
    }
  });
  
  // ========== ADICIONAR ITEM ==========
  
  function adicionarItem() {
    const codigo = codInput.value.trim();
    const produto = prodInput.value.trim();
    const precoTexto = precoInput.value.replace(/\./g, '').replace(',', '.');
    const preco = parseFloat(precoTexto);
    const qtd = parseInt(qtdInput.value);
    
    // Validações
    if (!codigo) {
      mostrarNotificacao('Digite o código do produto', 'aviso');
      codInput.focus();
      return;
    }
    
    if (!produto) {
      mostrarNotificacao('Busque o produto primeiro', 'aviso');
      btnBuscarProduto.click();
      return;
    }
    
    if (isNaN(preco) || preco <= 0) {
      mostrarNotificacao('Preço inválido', 'aviso');
      precoInput.focus();
      return;
    }
    
    if (qtd <= 0) {
      mostrarNotificacao('Quantidade deve ser maior que zero', 'aviso');
      qtdInput.focus();
      return;
    }
    
    // REMOVIDA A VALIDAÇÃO DE ESTOQUE AQUI
    // O backend vai validar no momento de finalizar a venda
    
    // Calcula subtotal
    const subtotal = preco * qtd;
    
    // Adiciona o item
    itens.push({
      codigo: codigo,
      produto: produto,
      quantidade: qtd,
      preco: preco,
      subtotal: subtotal
    });
    
    // Atualiza o total
    total += subtotal;
    totalSpan.textContent = `R$ ${formatarMoeda(total)}`;
    
    // Atualiza a tabela
    atualizarTabela();
    
    // Feedback
    mostrarNotificacao(`✓ Item adicionado: ${produto}`, 'sucesso');
    
    // Limpa os campos do produto
    codInput.value = '';
    limparCamposProduto();
    codInput.focus();
  }
  
  btnAdicionar.addEventListener('click', adicionarItem);
  
  qtdInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      adicionarItem();
    }
  });
  
  // ========== ATUALIZAR TABELA ==========
  
  function atualizarTabela() {
    if (itens.length === 0) {
      tabela.innerHTML = '<tr><td colspan="6" class="empty">Nenhum item adicionado</td></tr>';
      return;
    }
    
    tabela.innerHTML = '';
    itens.forEach((item, index) => {
      const tr = document.createElement('tr');
      tr.className = 'destaque-linha';
      tr.innerHTML = `
        <td>${item.codigo}</td>
        <td style="text-align: left;">${item.produto}</td>
        <td>${item.quantidade}</td>
        <td>R$ ${formatarMoeda(item.preco)}</td>
        <td>R$ ${formatarMoeda(item.subtotal)}</td>
        <td>
          <button class="btn-remover" onclick="removerItem(${index})">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      `;
      tabela.appendChild(tr);
    });
  }
  
  // Função global para remover item
  window.removerItem = function(index) {
    if (confirm('Deseja remover este item?')) {
      const itemRemovido = itens[index];
      total -= itemRemovido.subtotal;
      itens.splice(index, 1);
      
      totalSpan.textContent = `R$ ${formatarMoeda(total)}`;
      atualizarTabela();
      
      mostrarNotificacao('Item removido', 'info');
    }
  };
  
  // ========== CANCELAR VENDA ==========
  
  function cancelarVenda() {
    if (itens.length > 0) {
      if (!confirm('⚠️ Deseja realmente cancelar esta venda?\n\nTodos os itens serão removidos.')) {
        return;
      }
    }
    
    // Limpa tudo
    itens = [];
    total = 0;
    clienteId = null;
    estoqueAtual = {};
    
    cpfInput.value = '';
    nomeInput.value = '';
    dataInput.value = hoje;
    codInput.value = '';
    limparCamposProduto();
    
    totalSpan.textContent = 'R$ 0,00';
    atualizarTabela();
    
    mostrarNotificacao('Venda cancelada', 'info');
    cpfInput.focus();
  }
  
  btnCancelar.addEventListener('click', cancelarVenda);
  
  // ========== FINALIZAR VENDA ==========
  
  async function finalizarVenda() {
    // Validações
    if (itens.length === 0) {
      mostrarNotificacao('Adicione pelo menos um item à venda', 'aviso');
      codInput.focus();
      return;
    }
    
    // Confirmação
    const mensagemConfirmacao = `
Finalizar venda?

Total: R$ ${formatarMoeda(total)}
Itens: ${itens.length}
Cliente: ${nomeInput.value || 'Não identificado'}
    `.trim();
    
    if (!confirm(mensagemConfirmacao)) {
      return;
    }
    
    // Desabilita botões
    btnPagamento.disabled = true;
    btnPagamento.textContent = 'Processando...';
    btnCancelar.disabled = true;
    
    try {
      const response = await fetch('/venda/finalizar_venda/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
          cpf: cpfInput.value.trim(),
          itens: itens,
          total: total,
          observacoes: ''
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.mensagem) {
        mostrarNotificacao('✓ Venda finalizada! Redirecionando...', 'sucesso');
        
        // Pequeno delay para mostrar a mensagem
        setTimeout(() => {
          window.location.href = '/venda/pagamentos/';
        }, 1000);
      } else {
        throw new Error(data.erro || 'Erro ao finalizar venda');
      }
    } catch (error) {
      console.error('Erro ao finalizar venda:', error);
      mostrarNotificacao(error.message || 'Erro ao finalizar venda', 'erro');
      
      // Reabilita botões
      btnPagamento.disabled = false;
      btnPagamento.textContent = 'PAGAMENTO';
      btnCancelar.disabled = false;
    }
  }
  
  btnPagamento.addEventListener('click', finalizarVenda);
  
  // ========== ATALHOS DE TECLADO ==========
  
  document.addEventListener('keydown', (e) => {
    // F2: Buscar cliente
    if (e.key === 'F2') {
      e.preventDefault();
      cpfInput.focus();
      cpfInput.select();
    }
    
    // F3: Buscar produto
    if (e.key === 'F3') {
      e.preventDefault();
      codInput.focus();
      codInput.select();
    }
    
    // F4: Adicionar item
    if (e.key === 'F4') {
      e.preventDefault();
      if (codInput.value && prodInput.value && qtdInput.value > 0) {
        adicionarItem();
      }
    }
    
    // F9: Cancelar venda
    if (e.key === 'F9') {
      e.preventDefault();
      cancelarVenda();
    }
    
    // F12: Finalizar venda
    if (e.key === 'F12') {
      e.preventDefault();
      if (itens.length > 0) {
        finalizarVenda();
      }
    }
  });
  
  // ========== INICIALIZAÇÃO ==========
  
  // Foca no primeiro campo
  cpfInput.focus();
  
  // Log de atalhos no console
  console.log(`
╔════════════════════════════════════════╗
║      ATALHOS DO PONTO DE VENDAS        ║
╠════════════════════════════════════════╣
║ F2  - Buscar Cliente                   ║
║ F3  - Buscar Produto                   ║
║ F4  - Adicionar Item                   ║
║ F9  - Cancelar Venda                   ║
║ F12 - Finalizar Venda                  ║
╚════════════════════════════════════════╝
  `);
  
  mostrarNotificacao('Sistema PDV carregado. Pressione F2 para iniciar', 'info');
});