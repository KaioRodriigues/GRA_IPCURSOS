"""
Utilitários de validação
Funções para validar entradas de dados
"""

from datetime import datetime
from typing import Optional, Tuple


def validar_data_br(data_str: str) -> Tuple[bool, Optional[datetime]]:
    """
    Valida e converte uma data no formato DD/MM/AAAA
    
    Args:
        data_str: String com a data
        
    Returns:
        Tupla (válido: bool, data: datetime ou None)
    """
    if not data_str:
        return False, None
    
    try:
        # Tentar converter DD/MM/AAAA
        data = datetime.strptime(data_str, "%d/%m/%Y")
        return True, data
    except ValueError:
        return False, None


def validar_horario(horario_str: str) -> Tuple[bool, str]:
    """
    Valida um horário no formato HH:MM ou HH
    
    Args:
        horario_str: String com o horário
        
    Returns:
        Tupla (válido: bool, horário_formatado: str)
    """
    if not horario_str:
        return False, ""
    
    horario_str = horario_str.strip()
    
    # Se já tem :, validar formato HH:MM
    if ":" in horario_str:
        partes = horario_str.split(":")
        if len(partes) != 2:
            return False, ""
        
        try:
            hora = int(partes[0])
            minuto = int(partes[1])
            
            if 0 <= hora <= 23 and 0 <= minuto <= 59:
                return True, f"{hora:02d}:{minuto:02d}"
            else:
                return False, ""
        except ValueError:
            return False, ""
    
    # Se é apenas número, validar hora
    if horario_str.isdigit():
        hora = int(horario_str)
        if 0 <= hora <= 23:
            return True, f"{hora:02d}:00"
        else:
            return False, ""
    
    return False, ""


def validar_nome(nome: str) -> Tuple[bool, str]:
    """
    Valida um nome (não pode ser vazio)
    
    Args:
        nome: String com o nome
        
    Returns:
        Tupla (válido: bool, mensagem: str)
    """
    if not nome or nome.strip() == "":
        return False, "Nome não pode ser vazio"
    
    if len(nome.strip()) < 3:
        return False, "Nome deve ter pelo menos 3 caracteres"
    
    return True, ""


def auto_formatar_data(texto: str) -> str:
    """
    Adiciona automaticamente as barras na data enquanto o usuário digita
    
    Args:
        texto: Texto atual do campo
        
    Returns:
        Texto formatado com barras
    """
    # Remove tudo que não é número
    apenas_numeros = ''.join(filter(str.isdigit, texto))
    
    # Limita a 8 dígitos (DDMMAAAA)
    apenas_numeros = apenas_numeros[:8]
    
    # Adiciona as barras automaticamente
    if len(apenas_numeros) <= 2:
        return apenas_numeros
    elif len(apenas_numeros) <= 4:
        return f"{apenas_numeros[:2]}/{apenas_numeros[2:]}"
    else:
        return f"{apenas_numeros[:2]}/{apenas_numeros[2:4]}/{apenas_numeros[4:]}"


def auto_formatar_horario(texto: str) -> str:
    """
    Adiciona automaticamente os dois pontos no horário
    
    Args:
        texto: Texto atual do campo
        
    Returns:
        Texto formatado
    """
    # Remove tudo que não é número ou :
    limpo = ''.join(c for c in texto if c.isdigit() or c == ':')
    
    # Se já tem :, não fazer nada
    if ':' in limpo:
        return limpo
    
    # Se tem 2 ou mais dígitos, adicionar :00
    if len(limpo) >= 2:
        return f"{limpo[:2]}:{limpo[2:4] if len(limpo) > 2 else '00'}"
    
    return limpo
