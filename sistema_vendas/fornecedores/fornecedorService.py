from .models import Fornecedor
from django.core.exceptions import ValidationError
from django.db import IntegrityError


class FornecedorService:
    """
    Service para gerenciar operações de Fornecedores
    """
    
    @staticmethod
    def cadastrar_fornecedor(dados):
        """
        Cadastra um novo fornecedor no sistema
        
        Args:
            dados (dict): Dicionário com os dados do fornecedor
            
        Returns:
            tuple: (sucesso: bool, mensagem: str, fornecedor: Fornecedor ou None)
        """
        try:
            # Validação de campos obrigatórios
            if not dados.get('nome'):
                return False, "O nome do fornecedor é obrigatório", None
            
            if not dados.get('cnpj'):
                return False, "O CNPJ é obrigatório", None
            
            # Verifica se já existe fornecedor com o mesmo CNPJ
            cnpj = dados.get('cnpj').strip()
            if Fornecedor.objects.filter(cnpj=cnpj).exists():
                return False, "Já existe um fornecedor cadastrado com este CNPJ", None
            
            # Cria o fornecedor
            fornecedor = Fornecedor.objects.create(
                nome=dados.get('nome', '').strip(),
                cnpj=cnpj,
                email=dados.get('email', '').strip() or None,
                telefone=dados.get('telefone', '').strip() or None,
                celular=dados.get('celular', '').strip() or None,
                cep=dados.get('cep', '').strip() or None,
                endereco=dados.get('endereco', '').strip() or None,
                numero=dados.get('numero') or None,
                complemento=dados.get('complemento', '').strip() or None,
                bairro=dados.get('bairro', '').strip() or None,
                cidade=dados.get('cidade', '').strip() or None,
                estado=dados.get('estado', '').strip() or None,
            )
            
            return True, "Fornecedor cadastrado com sucesso!", fornecedor
            
        except ValidationError as e:
            return False, f"Erro de validação: {str(e)}", None
        except IntegrityError as e:
            return False, f"Erro de integridade: {str(e)}", None
        except Exception as e:
            return False, f"Erro ao cadastrar fornecedor: {str(e)}", None
    
    
    @staticmethod
    def editar_fornecedor(fornecedor_id, dados):
        """
        Edita um fornecedor existente
        
        Args:
            fornecedor_id (int): ID do fornecedor a ser editado
            dados (dict): Dicionário com os novos dados do fornecedor
            
        Returns:
            tuple: (sucesso: bool, mensagem: str, fornecedor: Fornecedor ou None)
        """
        try:
            # Busca o fornecedor
            try:
                fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            except Fornecedor.DoesNotExist:
                return False, "Fornecedor não encontrado", None
            
            # Validação de campos obrigatórios
            if not dados.get('nome'):
                return False, "O nome do fornecedor é obrigatório", None
            
            if not dados.get('cnpj'):
                return False, "O CNPJ é obrigatório", None
            
            # Verifica se o CNPJ já existe em outro fornecedor
            cnpj = dados.get('cnpj').strip()
            if Fornecedor.objects.filter(cnpj=cnpj).exclude(id=fornecedor_id).exists():
                return False, "Já existe outro fornecedor cadastrado com este CNPJ", None
            
            # Atualiza os dados do fornecedor
            fornecedor.nome = dados.get('nome', '').strip()
            fornecedor.cnpj = cnpj
            fornecedor.email = dados.get('email', '').strip() or None
            fornecedor.telefone = dados.get('telefone', '').strip() or None
            fornecedor.celular = dados.get('celular', '').strip() or None
            fornecedor.cep = dados.get('cep', '').strip() or None
            fornecedor.endereco = dados.get('endereco', '').strip() or None
            fornecedor.numero = dados.get('numero') or None
            fornecedor.complemento = dados.get('complemento', '').strip() or None
            fornecedor.bairro = dados.get('bairro', '').strip() or None
            fornecedor.cidade = dados.get('cidade', '').strip() or None
            fornecedor.estado = dados.get('estado', '').strip() or None
            
            fornecedor.save()
            
            return True, "Fornecedor atualizado com sucesso!", fornecedor
            
        except ValidationError as e:
            return False, f"Erro de validação: {str(e)}", None
        except IntegrityError as e:
            return False, f"Erro de integridade: {str(e)}", None
        except Exception as e:
            return False, f"Erro ao editar fornecedor: {str(e)}", None
    
    
    @staticmethod
    def buscar_fornecedor(fornecedor_id):
        """
        Busca um fornecedor pelo ID
        
        Args:
            fornecedor_id (int): ID do fornecedor
            
        Returns:
            Fornecedor ou None
        """
        try:
            fornecedor = Fornecedor.objects.filter(id=fornecedor_id).values()
            return fornecedor[0]
        except Fornecedor.DoesNotExist:
            return None
    
    
    @staticmethod
    def listar_fornecedores():
        """
        Lista todos os fornecedores
        
        Returns:
            QuerySet: Lista de fornecedores
        """
        return Fornecedor.objects.all().order_by('nome')
    
    
    @staticmethod
    def excluir_fornecedor(fornecedor_id):
        """
        Exclui um fornecedor (se não tiver compras associadas)
        
        Args:
            fornecedor_id (int): ID do fornecedor
            
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            
            # Verifica se o fornecedor tem compras associadas
            if fornecedor.compras.exists():
                return False, "Não é possível excluir um fornecedor com compras associadas"
            
            f = fornecedor.delete()
            print(f)
            return True, "Fornecedor excluído com sucesso!"
            
        except Fornecedor.DoesNotExist:
            return False, "Fornecedor não encontrado"
        except Exception as e:
            return False, f"Erro ao excluir fornecedor: {str(e)}"