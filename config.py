"""
Configuração do Sistema de Gestão de Alunos
Gerencia conexão com Supabase e configurações globais
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env (se existir)
load_dotenv()


class Config:
    """Classe de configuração do sistema"""
    
    # ============================================
    # CONFIGURAÇÕES DO SUPABASE
    # ============================================
    # IMPORTANTE: Substitua os valores abaixo pelas suas credenciais do Supabase
    # Ou crie um arquivo .env na raiz do projeto com:
    # SUPABASE_URL=sua_url_aqui
    # SUPABASE_KEY=sua_chave_aqui
    
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # ============================================
    # CONFIGURAÇÕES DA APLICAÇÃO
    # ============================================
    APP_NAME = "Sistema de Gestão de Alunos"
    APP_VERSION = "1.0.0"
    ORGANIZATION = "SistemaGestao"
    
    # ============================================
    # VALIDAÇÕES
    # ============================================
    @classmethod
    def validar_credenciais(cls) -> tuple[bool, str]:
        """
        Valida se as credenciais do Supabase foram configuradas
        
        Returns:
            tuple: (válido: bool, mensagem: str)
        """
        if not cls.SUPABASE_URL or cls.SUPABASE_URL == "":
            return False, "URL do Supabase não configurada"
        
        if not cls.SUPABASE_KEY or cls.SUPABASE_KEY == "":
            return False, "Chave do Supabase não configurada"
        
        if not cls.SUPABASE_URL.startswith("https://"):
            return False, "URL do Supabase deve começar com https://"
        
        return True, "Credenciais válidas"
    
    @classmethod
    def configurar_credenciais(cls, url: str, key: str):
        """
        Configura as credenciais do Supabase programaticamente
        
        Args:
            url: URL do projeto Supabase
            key: Chave anônima (anon key) do Supabase
        """
        cls.SUPABASE_URL = url
        cls.SUPABASE_KEY = key
        
        # Salvar no arquivo .env para persistência
        try:
            with open(".env", "w") as f:
                f.write(f"SUPABASE_URL={url}\n")
                f.write(f"SUPABASE_KEY={key}\n")
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")


# ============================================
# CONSTANTES DO SISTEMA
# ============================================

TIPOS_PLANO = ["Convencional", "Acelerado", "Flex"]
SITUACOES_ACADEMICAS = ["Regular", "Atrasado", "Adiantado", "Formado(a)"]
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
STATUS_ACAO = ["Pendente", "Concluída"]

# Opções de aulas (1 a 30)
OPCOES_AULAS = [str(i) for i in range(1, 31)]

# Opções de pagamento/parcelas (1 a 30 + Concluído)
OPCOES_PAGAMENTO = [str(i) for i in range(1, 31)] + ["Concluído"]
