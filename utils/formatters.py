"""
Utilitários de formatação
Funções para formatar datas, horários e outros dados
"""

from datetime import datetime, date
from typing import Optional
import json


def formatar_data_br(data: Optional[date]) -> str:
    """
    Formata uma data para o formato brasileiro DD/MM/AAAA
    
    Args:
        data: Objeto date ou None
        
    Returns:
        String formatada ou vazio
    """
    if not data:
        return ""
    
    if isinstance(data, str):
        try:
            data = datetime.fromisoformat(data).date()
        except:
            return data
    
    return data.strftime("%d/%m/%Y")


def formatar_horario(horario: str) -> str:
    """
    Formata um horário para HH:MM
    Se receber apenas números, adiciona :00
    
    Args:
        horario: String com horário
        
    Returns:
        Horário formatado
    """
    if not horario:
        return ""
    
    # Remove espaços
    horario = horario.strip()
    
    # Se já está no formato HH:MM, retorna
    if ":" in horario:
        return horario
    
    # Se é apenas número, adiciona :00
    if horario.isdigit():
        return f"{horario.zfill(2)}:00"
    
    return horario


def formatar_data_hora(data_hora: Optional[datetime]) -> str:
    """
    Formata data e hora para o formato brasileiro DD/MM/AAAA HH:MM
    
    Args:
        data_hora: Objeto datetime ou None
        
    Returns:
        String formatada ou vazio
    """
    if not data_hora:
        return ""
    
    if isinstance(data_hora, str):
        try:
            data_hora = datetime.fromisoformat(data_hora.replace('Z', '+00:00'))
        except:
            return data_hora
    
    return data_hora.strftime("%d/%m/%Y %H:%M")


def formatar_dia_horario(dia_horario_json: Optional[str]) -> str:
    """
    Formata o JSON de dia/horário para exibição legível
    Suporta múltiplos horários por dia
    
    Args:
        dia_horario_json: String JSON com dias e horários
        
    Returns:
        String formatada (ex: "Seg 20:00, Qua 18:00/19:00")
    """
    if not dia_horario_json:
        return ""
    
    try:
        if isinstance(dia_horario_json, str):
            dados = json.loads(dia_horario_json)
        else:
            dados = dia_horario_json
        
        # Abreviações dos dias
        abrev = {
            "Segunda": "Seg",
            "Terça": "Ter",
            "Quarta": "Qua",
            "Quinta": "Qui",
            "Sexta": "Sex",
            "Sábado": "Sáb",
            "Domingo": "Dom"
        }
        
        resultado = []
        for dia, horario in dados.items():
            dia_abrev = abrev.get(dia, dia[:3])
            
            # Se for lista de horários, juntar com /
            if isinstance(horario, list):
                horarios_str = "/".join(horario)
                resultado.append(f"{dia_abrev} {horarios_str}")
            else:
                resultado.append(f"{dia_abrev} {horario}")
        
        return ", ".join(resultado)
    except:
        return str(dia_horario_json)


def truncar_texto(texto: str, max_length: int = 50) -> str:
    """
    Trunca um texto longo adicionando reticências
    
    Args:
        texto: Texto a ser truncado
        max_length: Tamanho máximo
        
    Returns:
        Texto truncado
    """
    if not texto:
        return ""
    
    if len(texto) <= max_length:
        return texto
    
    return texto[:max_length - 3] + "..."
