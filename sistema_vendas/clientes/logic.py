from .models import Cliente
from django.db.models import Q


class ClienteLogic:
    """
    Classe de lógica de negócios para operações com Cliente
    """
    
    @staticmethod
    def listar_clientes(search=''):
        """
        Lista todos os clientes com busca opcional
        
        Args:
            search (str): Termo de busca para filtrar clientes
            
        Returns:
            list: Lista de dicionários com dados dos clientes
        """
        try:
            # Query base
            queryset = Cliente.objects.all()
            
            # Aplicar filtro de busca se fornecido
            if search:
                queryset = queryset.filter(
                    Q(nome__icontains=search) |
                    Q(cpf__icontains=search) |
                    Q(email__icontains=search) |
                    Q(telefone__icontains=search) |
                    Q(celular__icontains=search) |
                    Q(cidade__icontains=search)
                )
            
            # Ordenar por nome
            queryset = queryset.order_by('nome')
            
            # Converter para lista de dicionários
            clientes = []
            for cliente in queryset:
                clientes.append({
                    'id': cliente.id,
                    'nome': cliente.nome,
                    'rg': cliente.rg,
                    'cpf': cliente.cpf,
                    'email': cliente.email,
                    'telefone': cliente.telefone,
                    'celular': cliente.celular,
                    'cep': cliente.cep,
                    'endereco': cliente.endereco,
                    'numero': cliente.numero,
                    'complemento': cliente.complemento,
                    'bairro': cliente.bairro,
                    'cidade': cliente.cidade,
                    'uf': cliente.uf,
                })
            
            return clientes
            
        except Exception as e:
            raise Exception(f"Erro ao listar clientes: {str(e)}")
    
    @staticmethod
    def obter_cliente(cliente_id):
        """
        Obtém um cliente específico pelo ID
        
        Args:
            cliente_id (int): ID do cliente
            
        Returns:
            dict: Dicionário com dados do cliente ou None se não encontrado
        """
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            
            return {
                'id': cliente.id,
                'nome': cliente.nome,
                'rg': cliente.rg,
                'cpf': cliente.cpf,
                'email': cliente.email,
                'telefone': cliente.telefone,
                'celular': cliente.celular,
                'cep': cliente.cep,
                'endereco': cliente.endereco,
                'numero': cliente.numero,
                'complemento': cliente.complemento,
                'bairro': cliente.bairro,
                'cidade': cliente.cidade,
                'uf': cliente.uf,
            }
            
        except Cliente.DoesNotExist:
            return None
        except Exception as e:
            raise Exception(f"Erro ao obter cliente: {str(e)}")
    
    @staticmethod
    def criar_cliente(dados):
        """
        Cria um novo cliente
        
        Args:
            dados (dict): Dicionário com os dados do cliente
            
        Returns:
            dict: Dicionário com dados do cliente criado
        """
        try:
            # Validar CPF único
            if Cliente.objects.filter(cpf=dados['cpf']).exists():
                raise Exception("CPF já cadastrado no sistema")
            
            cliente = Cliente.objects.create(
                nome=dados['nome'],
                rg=dados.get('rg'),
                cpf=dados['cpf'],
                email=dados.get('email'),
                telefone=dados.get('telefone'),
                celular=dados.get('celular'),
                cep=dados.get('cep'),
                endereco=dados.get('endereco'),
                numero=dados.get('numero'),
                complemento=dados.get('complemento'),
                bairro=dados.get('bairro'),
                cidade=dados.get('cidade'),
                uf=dados.get('uf'),
            )
            
            return {
                'id': cliente.id,
                'nome': cliente.nome,
                'cpf': cliente.cpf,
            }
            
        except Exception as e:
            raise Exception(f"Erro ao criar cliente: {str(e)}")
    
    @staticmethod
    def atualizar_cliente(cliente_id, dados):
        """
        Atualiza um cliente existente
        
        Args:
            cliente_id (int): ID do cliente
            dados (dict): Dicionário com os dados a serem atualizados
            
        Returns:
            dict: Dicionário com dados do cliente atualizado ou None se não encontrado
        """
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            
            # Validar CPF único (exceto o próprio cliente)
            if 'cpf' in dados and dados['cpf'] != cliente.cpf:
                if Cliente.objects.filter(cpf=dados['cpf']).exclude(id=cliente_id).exists():
                    raise Exception("CPF já cadastrado no sistema")
            
            # Atualizar campos
            for campo, valor in dados.items():
                if hasattr(cliente, campo):
                    setattr(cliente, campo, valor)
            
            cliente.save()
            
            return {
                'id': cliente.id,
                'nome': cliente.nome,
                'cpf': cliente.cpf,
            }
            
        except Cliente.DoesNotExist:
            return None
        except Exception as e:
            raise Exception(f"Erro ao atualizar cliente: {str(e)}")
    
    @staticmethod
    def deletar_cliente(cliente_id):
        """
        Deleta um cliente
        
        Args:
            cliente_id (int): ID do cliente
            
        Returns:
            bool: True se deletado com sucesso, False se não encontrado
        """
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            cliente.delete()
            return True
            
        except Cliente.DoesNotExist:
            return False
        except Exception as e:
            raise Exception(f"Erro ao deletar cliente: {str(e)}")
    
    @staticmethod
    def validar_cpf(cpf):
        """
        Valida se o CPF está em formato válido (básico)
        
        Args:
            cpf (str): CPF a ser validado
            
        Returns:
            bool: True se válido, False caso contrário
        """
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se não são todos dígitos iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Validação dos dígitos verificadores
        def calcular_digito(cpf_parcial, peso_inicial):
            soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(peso_inicial, 1, -1)))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)
        
        # Valida primeiro dígito
        if cpf[9] != calcular_digito(cpf[:9], 10):
            return False
        
        # Valida segundo dígito
        if cpf[10] != calcular_digito(cpf[:10], 11):
            return False
        
        return True