"""
Gerenciador de Banco de Dados
Classe responsável por todas as operações com o Supabase
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from supabase import create_client, Client
from config import Config
import json


class DatabaseManager:
    """Gerenciador de operações com o banco de dados Supabase"""
    
    def __init__(self):
        """Inicializa a conexão com o Supabase"""
        self.client: Optional[Client] = None
        self.conectado = False
        
    def conectar(self) -> tuple[bool, str]:
        """
        Estabelece conexão com o Supabase
        
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            valido, mensagem = Config.validar_credenciais()
            if not valido:
                return False, mensagem
            
            self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            self.conectado = True
            return True, "Conectado com sucesso"
        except Exception as e:
            self.conectado = False
            return False, f"Erro ao conectar: {str(e)}"
    
    # ============================================
    # OPERAÇÕES COM UNIDADES
    # ============================================
    
    def listar_unidades(self) -> List[Dict[str, Any]]:
        """Lista todas as unidades"""
        try:
            response = self.client.table("unidades").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Erro ao listar unidades: {e}")
            return []
    
    # ============================================
    # OPERAÇÕES COM INSTRUTORES
    # ============================================
    
    def listar_instrutores(self, unidade_id: int, apenas_ativos: bool = True) -> List[Dict[str, Any]]:
        """Lista instrutores de uma unidade"""
        try:
            query = self.client.table("instrutores").select("*").eq("unidade_id", unidade_id)
            if apenas_ativos:
                query = query.eq("ativo", True)
            response = query.order("nome").execute()
            return response.data
        except Exception as e:
            print(f"Erro ao listar instrutores: {e}")
            return []
    
    def adicionar_instrutor(self, nome: str, unidade_id: int) -> tuple[bool, str]:
        """Adiciona um novo instrutor"""
        try:
            data = {
                "nome": nome,
                "unidade_id": unidade_id,
                "ativo": True
            }
            self.client.table("instrutores").insert(data).execute()
            return True, "Instrutor adicionado com sucesso"
        except Exception as e:
            return False, f"Erro ao adicionar instrutor: {str(e)}"
    
    def excluir_instrutor(self, instrutor_id: int) -> tuple[bool, str]:
        """Marca um instrutor como inativo"""
        try:
            self.client.table("instrutores").update({"ativo": False}).eq("id", instrutor_id).execute()
            return True, "Instrutor excluído com sucesso"
        except Exception as e:
            return False, f"Erro ao excluir instrutor: {str(e)}"
    
    def obter_instrutor(self, instrutor_id: int) -> Optional[Dict[str, Any]]:
        """Obtém dados de um instrutor específico"""
        try:
            response = self.client.table("instrutores").select("*").eq("id", instrutor_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao obter instrutor: {e}")
            return None
    
    # ============================================
    # OPERAÇÕES COM ALUNOS
    # ============================================
    
    def listar_alunos(self, unidade_id: int, incluir_arquivados: bool = False) -> List[Dict[str, Any]]:
        """Lista alunos de uma unidade"""
        try:
            query = self.client.table("alunos").select(
                "*, instrutores(nome)"
            ).eq("unidade_id", unidade_id)
            
            if not incluir_arquivados:
                query = query.eq("arquivado", False)
            
            response = query.order("nome").execute()
            return response.data
        except Exception as e:
            print(f"Erro ao listar alunos: {e}")
            return []
    
    def adicionar_aluno(self, dados: Dict[str, Any]) -> tuple[bool, str]:
        """Adiciona um novo aluno"""
        try:
            # Converter data_inicio para string no formato ISO
            if isinstance(dados.get('data_inicio'), date):
                dados['data_inicio'] = dados['data_inicio'].isoformat()
            
            # Garantir que dia_horario seja JSON
            if 'dia_horario' in dados and isinstance(dados['dia_horario'], dict):
                dados['dia_horario'] = json.dumps(dados['dia_horario'])
            
            self.client.table("alunos").insert(dados).execute()
            return True, "Aluno adicionado com sucesso"
        except Exception as e:
            return False, f"Erro ao adicionar aluno: {str(e)}"
    
    def atualizar_aluno(self, aluno_id: int, dados: Dict[str, Any]) -> tuple[bool, str]:
        """Atualiza dados de um aluno"""
        try:
            # Converter data_inicio para string no formato ISO
            if isinstance(dados.get('data_inicio'), date):
                dados['data_inicio'] = dados['data_inicio'].isoformat()
            
            # Garantir que dia_horario seja JSON
            if 'dia_horario' in dados and isinstance(dados['dia_horario'], dict):
                dados['dia_horario'] = json.dumps(dados['dia_horario'])
            
            self.client.table("alunos").update(dados).eq("id", aluno_id).execute()
            return True, "Aluno atualizado com sucesso"
        except Exception as e:
            return False, f"Erro ao atualizar aluno: {str(e)}"
    
    def obter_aluno(self, aluno_id: int) -> Optional[Dict[str, Any]]:
        """Obtém dados de um aluno específico"""
        try:
            response = self.client.table("alunos").select("*").eq("id", aluno_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao obter aluno: {e}")
            return None
    
    def arquivar_aluno(self, aluno_id: int, arquivar: bool = True) -> tuple[bool, str]:
        """Arquiva ou desarquiva um aluno"""
        try:
            self.client.table("alunos").update({"arquivado": arquivar}).eq("id", aluno_id).execute()
            acao = "arquivado" if arquivar else "desarquivado"
            return True, f"Aluno {acao} com sucesso"
        except Exception as e:
            return False, f"Erro ao arquivar aluno: {str(e)}"
    
    def contar_acoes_pendentes(self, aluno_id: int) -> int:
        """Conta quantas ações pendentes um aluno tem"""
        try:
            response = self.client.table("acoes").select(
                "id", count="exact"
            ).eq("aluno_id", aluno_id).eq("status", "Pendente").execute()
            return response.count if response.count else 0
        except Exception as e:
            print(f"Erro ao contar ações pendentes: {e}")
            return 0
    
    # ============================================
    # OPERAÇÕES COM AÇÕES
    # ============================================
    
    def listar_acoes(self, aluno_id: int) -> List[Dict[str, Any]]:
        """Lista todas as ações de um aluno"""
        try:
            response = self.client.table("acoes").select(
                "*, instrutores(nome)"
            ).eq("aluno_id", aluno_id).order("data_proposta", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Erro ao listar ações: {e}")
            return []
    
    def adicionar_acao(self, aluno_id: int, acao_proposta: str, instrutor_resp_id: int) -> tuple[bool, str]:
        """Adiciona uma nova ação para um aluno"""
        try:
            data = {
                "aluno_id": aluno_id,
                "acao_proposta": acao_proposta,
                "status": "Pendente",
                "instrutor_resp_id": instrutor_resp_id,
                "data_proposta": datetime.now().date().isoformat()
            }
            self.client.table("acoes").insert(data).execute()
            return True, "Ação proposta com sucesso"
        except Exception as e:
            return False, f"Erro ao adicionar ação: {str(e)}"
    
    def concluir_acao(self, acao_id: int) -> tuple[bool, str]:
        """Marca uma ação como concluída"""
        try:
            data = {
                "status": "Concluída",
                "data_conclusao": datetime.now().date().isoformat()
            }
            self.client.table("acoes").update(data).eq("id", acao_id).execute()
            return True, "Ação marcada como concluída"
        except Exception as e:
            return False, f"Erro ao concluir ação: {str(e)}"
    
    # ============================================
    # OPERAÇÕES COM LOGS
    # ============================================
    
    def adicionar_log(self, instrutor_id: int, atividade: str, unidade_id: int) -> bool:
        """Adiciona um registro de log"""
        try:
            data = {
                "instrutor_id": instrutor_id,
                "atividade": atividade,
                "unidade_id": unidade_id,
                "data_hora": datetime.now().isoformat()
            }
            self.client.table("logs").insert(data).execute()
            return True
        except Exception as e:
            print(f"Erro ao adicionar log: {e}")
            return False
    
    def listar_logs(self, unidade_id: int, limite: int = 100) -> List[Dict[str, Any]]:
        """Lista logs de uma unidade"""
        try:
            response = self.client.table("logs").select(
                "*, instrutores(nome)"
            ).eq("unidade_id", unidade_id).order(
                "data_hora", desc=True
            ).limit(limite).execute()
            return response.data
        except Exception as e:
            print(f"Erro ao listar logs: {e}")
            return []


# Instância global do gerenciador de banco de dados
db = DatabaseManager()
