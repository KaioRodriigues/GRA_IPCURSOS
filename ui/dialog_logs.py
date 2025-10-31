"""
Dialog para Ver Logs
Exibe o histórico de atividades do sistema
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSpinBox
)
from PySide6.QtCore import Qt
from database import db
from ui.styles import aplicar_classe_botao, aplicar_classe_label
from utils.formatters import formatar_data_hora


class DialogLogs(QDialog):
    """Dialog para visualizar logs do sistema"""
    
    def __init__(self, unidade_id: int, parent=None):
        super().__init__(parent)
        self.unidade_id = unidade_id
        self.logs = []
        
        self.init_ui()
        self.carregar_logs()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("Histórico de Logs")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Histórico de Atividades")
        aplicar_classe_label(titulo, "subtitle")
        layout.addWidget(titulo)
        
        # Descrição
        descricao = QLabel(
            "Este é o registro de todas as atividades realizadas no sistema."
        )
        descricao.setWordWrap(True)
        aplicar_classe_label(descricao, "info")
        layout.addWidget(descricao)
        
        # Controle de limite
        layout_controle = QHBoxLayout()
        
        label_limite = QLabel("Exibir últimos:")
        layout_controle.addWidget(label_limite)
        
        self.spin_limite = QSpinBox()
        self.spin_limite.setMinimum(10)
        self.spin_limite.setMaximum(1000)
        self.spin_limite.setValue(100)
        self.spin_limite.setSingleStep(50)
        layout_controle.addWidget(self.spin_limite)
        
        label_registros = QLabel("registros")
        layout_controle.addWidget(label_registros)
        
        layout_controle.addStretch()
        
        btn_aplicar = QPushButton("Aplicar")
        btn_aplicar.clicked.connect(self.carregar_logs)
        layout_controle.addWidget(btn_aplicar)
        
        layout.addLayout(layout_controle)
        
        # Tabela de logs
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels([
            "Instrutor", "Atividade", "Data e Hora"
        ])
        
        # Configurações da tabela
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        
        # Ajustar colunas
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Instrutor
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Atividade
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Data e Hora
        
        layout.addWidget(self.tabela)
        
        # Botões de ação
        layout_botoes = QHBoxLayout()
        
        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.clicked.connect(self.carregar_logs)
        layout_botoes.addWidget(btn_atualizar)
        
        btn_fechar = QPushButton("Fechar")
        aplicar_classe_botao(btn_fechar, "secondary")
        btn_fechar.clicked.connect(self.accept)
        layout_botoes.addWidget(btn_fechar)
        
        layout.addLayout(layout_botoes)
        
        # Label de status
        self.label_status = QLabel("")
        aplicar_classe_label(self.label_status, "info")
        layout.addWidget(self.label_status)
        
        self.setLayout(layout)
        
    def carregar_logs(self):
        """Carrega os logs do banco de dados"""
        limite = self.spin_limite.value()
        self.logs = db.listar_logs(self.unidade_id, limite=limite)
        
        self.tabela.setRowCount(0)
        
        for log in self.logs:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # Instrutor
            instrutor_nome = "Sistema"
            if log.get('instrutores'):
                instrutor_nome = log['instrutores'].get('nome', 'Sistema')
            self.tabela.setItem(row, 0, QTableWidgetItem(instrutor_nome))
            
            # Atividade
            atividade = log.get('atividade', '')
            self.tabela.setItem(row, 1, QTableWidgetItem(atividade))
            
            # Data e Hora
            data_hora = formatar_data_hora(log.get('data_hora'))
            self.tabela.setItem(row, 2, QTableWidgetItem(data_hora))
        
        self.label_status.setText(f"Exibindo {len(self.logs)} registro(s) de log")
