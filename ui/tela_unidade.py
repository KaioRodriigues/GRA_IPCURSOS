"""
Tela de Seleção de Unidades
Primeira tela do sistema onde o usuário escolhe entre Ipiaú e Irecê
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QSettings
from PySide6.QtGui import QFont
from database import db
from ui.styles import aplicar_classe_label


class TelaUnidade(QWidget):
    """Tela para seleção da unidade (Ipiaú ou Irecê)"""
    
    # Signal emitido quando uma unidade é selecionada
    unidade_selecionada = Signal(int, str)  # (id, nome)
    
    def __init__(self):
        super().__init__()
        self.unidades = []
        self.settings = QSettings("SistemaGestao", "GestaoAlunos")
        self.init_ui()
        self.restaurar_geometria()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("Sistema de Gestão de Alunos - Seleção de Unidade")
        self.setMinimumSize(600, 400)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Título
        titulo = QLabel("Sistema de Gestão de Alunos")
        aplicar_classe_label(titulo, "title")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Selecione a Unidade")
        aplicar_classe_label(subtitulo, "subtitle")
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)
        
        # Espaçador
        layout.addStretch()
        
        # Container para os botões das unidades
        self.container_botoes = QVBoxLayout()
        self.container_botoes.setSpacing(15)
        layout.addLayout(self.container_botoes)
        
        # Espaçador
        layout.addStretch()
        
        # Label de status
        self.label_status = QLabel("")
        aplicar_classe_label(self.label_status, "info")
        self.label_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_status)
        
        self.setLayout(layout)
        
    def showEvent(self, event):
        """Evento chamado quando a janela é exibida"""
        super().showEvent(event)
        self.carregar_unidades()
        
    def carregar_unidades(self):
        """Carrega as unidades do banco de dados"""
        # Limpar botões existentes
        while self.container_botoes.count():
            item = self.container_botoes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Conectar ao banco se necessário
        if not db.conectado:
            sucesso, mensagem = db.conectar()
            if not sucesso:
                self.label_status.setText(f"Erro: {mensagem}")
                self.mostrar_erro("Erro de Conexão", mensagem)
                return
        
        # Buscar unidades
        self.unidades = db.listar_unidades()
        
        if not self.unidades:
            self.label_status.setText("Nenhuma unidade encontrada")
            return
        
        # Criar botão para cada unidade
        for unidade in self.unidades:
            botao = QPushButton(unidade['nome'])
            botao.setMinimumHeight(60)
            botao.setFont(QFont("Segoe UI", 14, QFont.Bold))
            botao.clicked.connect(lambda checked, u=unidade: self.selecionar_unidade(u))
            self.container_botoes.addWidget(botao)
        
        self.label_status.setText(f"{len(self.unidades)} unidade(s) disponível(is)")
        
    def selecionar_unidade(self, unidade: dict):
        """
        Seleciona uma unidade e emite o signal
        
        Args:
            unidade: Dicionário com dados da unidade
        """
        self.unidade_selecionada.emit(unidade['id'], unidade['nome'])
        
    def mostrar_erro(self, titulo: str, mensagem: str):
        """Exibe uma mensagem de erro"""
        QMessageBox.critical(self, titulo, mensagem)
        
    def closeEvent(self, event):
        """Salva a geometria da janela ao fechar"""
        self.salvar_geometria()
        super().closeEvent(event)
        
    def salvar_geometria(self):
        """Salva tamanho e posição da janela"""
        self.settings.setValue("tela_unidade/geometry", self.saveGeometry())
        
    def restaurar_geometria(self):
        """Restaura tamanho e posição da janela"""
        geometry = self.settings.value("tela_unidade/geometry")
        if geometry:
            self.restoreGeometry(geometry)
