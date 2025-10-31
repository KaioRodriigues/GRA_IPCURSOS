"""
Tela Principal
Lista de alunos com todas as funcionalidades principais
Refatorado para usar QStyledItemDelegate para colorir a linha inteira,
resolvendo conflitos de cores no Qt.
Corrigido o erro de atributo no QStyledItemDelegate.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem,
    QStyle # Adicionado para corrigir o erro State_Selected
)
from PySide6.QtCore import Qt, QSettings, QModelIndex
from PySide6.QtGui import QColor, QPainter
from database import db
from ui.styles import aplicar_classe_label, aplicar_classe_botao
from ui.dialog_aluno import DialogAluno
from utils.formatters import truncar_texto
import json


# ==============================================================================
# DELEGATE PERSONALIZADO PARA PINTAR A LINHA INTEIRA
# ==============================================================================

class LinhaColoridaDelegate(QStyledItemDelegate):
    """
    Delegate para pintar a linha inteira do QTableWidget com a cor
    definida no Qt.BackgroundRole do primeiro item da linha.
    """
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        # A cor de fundo é definida no item da primeira coluna (coluna 0)
        # e armazenada no Qt.BackgroundRole.
        
        # Se a coluna não for a primeira, pegamos o índice da primeira coluna
        if index.column() != 0:
            first_column_index = index.sibling(index.row(), 0)
            background_color = first_column_index.data(Qt.BackgroundRole)
        else:
            background_color = index.data(Qt.BackgroundRole)

        # Se houver uma cor de fundo definida, pintamos a linha inteira
        if background_color:
            painter.save()
            
            # Pinta o fundo da linha inteira
            painter.fillRect(option.rect, background_color)
            
            # Se a linha estiver selecionada, o estilo padrão de seleção
            # será aplicado sobre a cor de fundo.
            # CORREÇÃO: Usar QStyle.State_Selected em vez de QStyleOptionViewItem.State_Selected
            if option.state & QStyle.State_Selected:
                # Usa o estilo padrão para desenhar a seleção
                # É importante chamar o super().paint para que o estilo de seleção seja desenhado
                super().paint(painter, option, index)
            else:
                # Se não estiver selecionado, desenha o item normalmente
                # (texto, ícone, etc.) sobre o fundo colorido.
                super().paint(painter, option, index)
            
            painter.restore()
        else:
            # Se não houver cor de fundo, usa o comportamento padrão
            super().paint(painter, option, index)


# ==============================================================================
# TELA PRINCIPAL
# ==============================================================================

class TelaPrincipal(QWidget):
    """Tela principal com lista de alunos"""
    
    # Definição das cores para fácil manutenção
    COR_ACOES_PENDENTES = QColor(255, 100, 100)  # Vermelho mais forte
    COR_FORMADOS = QColor(100, 150, 255)         # Azul mais forte
    COR_ADIANTADO_ATRASADO = QColor(255, 255, 100) # Amarelo mais forte
    
    def __init__(self, unidade_id: int, unidade_nome: str, instrutor_id: int, instrutor_nome: str):
        super().__init__()
        self.unidade_id = unidade_id
        self.unidade_nome = unidade_nome
        self.instrutor_id = instrutor_id
        self.instrutor_nome = instrutor_nome
        self.alunos = []
        self.mostrar_formados = False  # Estado do botão de mostrar/ocultar formados
        self.settings = QSettings("SistemaGestao", "GestaoAlunos")
        
        self.init_ui()
        self.restaurar_geometria()
        self.atualizar_lista()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle(f"Sistema de Gestão de Alunos - {self.unidade_nome}")
        self.setMinimumSize(1200, 700)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Informações da sessão
        info_layout = QVBoxLayout()
        
        titulo = QLabel(f"Unidade: {self.unidade_nome}")
        aplicar_classe_label(titulo, "title")
        info_layout.addWidget(titulo)
        
        subtitulo = QLabel(f"Instrutor: {self.instrutor_nome}")
        aplicar_classe_label(subtitulo, "subtitle")
        info_layout.addWidget(subtitulo)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Tabela de alunos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels([
            "Nome", "Situação", "Observação", "Ações Pendentes", "Instrutor(a)"
        ])
        
        # Configurações da tabela
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        
        # Aplica o delegate personalizado
        self.tabela.setItemDelegate(LinhaColoridaDelegate(self.tabela))
        
        # Ajustar colunas
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nome
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Situação
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Observação
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Ações Pendentes
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Instrutor
        
        layout.addWidget(self.tabela)
        
        # Botões de ação
        botoes_layout = QHBoxLayout()
        
        btn_adicionar = QPushButton("Adicionar Aluno")
        aplicar_classe_botao(btn_adicionar, "success")
        btn_adicionar.clicked.connect(self.adicionar_aluno)
        botoes_layout.addWidget(btn_adicionar)
        
        btn_editar = QPushButton("Editar Aluno")
        btn_editar.clicked.connect(self.editar_aluno)
        botoes_layout.addWidget(btn_editar)
        
        btn_acoes = QPushButton("Gerenciar Ações")
        btn_acoes.clicked.connect(self.gerenciar_acoes)
        botoes_layout.addWidget(btn_acoes)
        
        self.btn_arquivados = QPushButton("Mostrar Formados(a)")
        aplicar_classe_botao(self.btn_arquivados, "secondary")
        self.btn_arquivados.clicked.connect(self.alternar_formados)
        botoes_layout.addWidget(self.btn_arquivados)
        
        btn_atualizar = QPushButton("Atualizar Lista")
        btn_atualizar.clicked.connect(self.atualizar_lista)
        botoes_layout.addWidget(btn_atualizar)
        
        btn_logs = QPushButton("Ver Log")
        aplicar_classe_botao(btn_logs, "secondary")
        btn_logs.clicked.connect(self.ver_logs)
        botoes_layout.addWidget(btn_logs)
        
        layout.addLayout(botoes_layout)
        
        # Label de status
        self.label_status = QLabel("")
        aplicar_classe_label(self.label_status, "info")
        layout.addWidget(self.label_status)
        
        self.setLayout(layout)
        
    def atualizar_lista(self):
        """Atualiza a lista de alunos"""
        self.alunos = db.listar_alunos(self.unidade_id, incluir_arquivados=self.mostrar_formados)
        
        self.tabela.setRowCount(0)
        
        for aluno in self.alunos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # 1. Determinar a cor da linha
            situacao = aluno.get('situacao_academica', '')
            acoes_pendentes = db.contar_acoes_pendentes(aluno['id'])
            
            cor_linha = None
            if acoes_pendentes > 0:
                # Vermelho para ações pendentes (prioridade máxima)
                cor_linha = self.COR_ACOES_PENDENTES
            elif situacao == "Formado(a)":
                # Azul para formados
                cor_linha = self.COR_FORMADOS
            elif situacao in ["Atrasado", "Adiantado"]:
                # Amarelo para atrasado e adiantado
                cor_linha = self.COR_ADIANTADO_ATRASADO
            
            # 2. Criar e configurar os itens da tabela
            
            # Nome (Coluna 0) - Armazena a cor de fundo e o ID do aluno
            item_nome = QTableWidgetItem(aluno['nome'])
            item_nome.setData(Qt.UserRole, aluno['id'])
            if cor_linha:
                # A cor é definida apenas no primeiro item (coluna 0)
                # O delegate usará essa cor para pintar a linha inteira
                item_nome.setData(Qt.BackgroundRole, cor_linha)
            self.tabela.setItem(row, 0, item_nome)
            
            # Situação (Coluna 1)
            item_situacao = QTableWidgetItem(situacao)
            self.tabela.setItem(row, 1, item_situacao)
            
            # Observação (Coluna 2)
            obs = truncar_texto(aluno.get('observacoes', ''), 50)
            item_obs = QTableWidgetItem(obs)
            self.tabela.setItem(row, 2, item_obs)
            
            # Ações Pendentes (Coluna 3)
            item_acoes = QTableWidgetItem(str(acoes_pendentes))
            self.tabela.setItem(row, 3, item_acoes)
            
            # Instrutor (Coluna 4)
            instrutor_nome = ""
            if aluno.get('instrutores'):
                instrutor_nome = aluno['instrutores'].get('nome', '')
            item_instrutor = QTableWidgetItem(instrutor_nome)
            self.tabela.setItem(row, 4, item_instrutor)
            
            # 3. Aplicar a cor do texto (opcional, para melhor contraste)
            # Se a cor de fundo for muito escura, podemos mudar a cor do texto para branco.
            if cor_linha and cor_linha in [self.COR_ACOES_PENDENTES, self.COR_FORMADOS]:
                for col in range(self.tabela.columnCount()):
                    item = self.tabela.item(row, col)
                    if item:
                        item.setForeground(QColor(255, 255, 255)) # Texto branco
        
        self.label_status.setText(f"Total: {len(self.alunos)} aluno(s)")
        
    def adicionar_aluno(self):
        """Abre o dialog para adicionar um novo aluno"""
        dialog = DialogAluno(self.unidade_id, self.instrutor_id, parent=self)
        if dialog.exec() == DialogAluno.Accepted:
            self.atualizar_lista()
            
    def editar_aluno(self):
        """Abre o dialog para editar o aluno selecionado"""
        linha_selecionada = self.tabela.currentRow()
        
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno para editar")
            return
        
        aluno_id = self.tabela.item(linha_selecionada, 0).data(Qt.UserRole)
        
        dialog = DialogAluno(self.unidade_id, self.instrutor_id, aluno_id, parent=self)
        if dialog.exec() == DialogAluno.Accepted:
            self.atualizar_lista()
            
    def gerenciar_acoes(self):
        """Abre o dialog para gerenciar ações do aluno selecionado"""
        linha_selecionada = self.tabela.currentRow()
        
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno para gerenciar ações")
            return
        
        aluno_id = self.tabela.item(linha_selecionada, 0).data(Qt.UserRole)
        aluno_nome = self.tabela.item(linha_selecionada, 0).text()
        
        # Importar aqui para evitar importação circular
        from ui.dialog_acoes import DialogAcoes
        
        dialog = DialogAcoes(aluno_id, aluno_nome, self.instrutor_id, self.unidade_id, parent=self)
        if dialog.exec() == DialogAcoes.Accepted:
            self.atualizar_lista()
            
    def alternar_formados(self):
        """Alterna entre mostrar e ocultar alunos formados"""
        self.mostrar_formados = not self.mostrar_formados
        
        if self.mostrar_formados:
            self.btn_arquivados.setText("Ocultar Formados(a)")
        else:
            self.btn_arquivados.setText("Mostrar Formados(a)")
        
        self.atualizar_lista()
            
    def ver_logs(self):
        """Abre o dialog para ver os logs"""
        # Importar aqui para evitar importação circular
        from ui.dialog_logs import DialogLogs
        
        dialog = DialogLogs(self.unidade_id, parent=self)
        dialog.exec()
        
    def closeEvent(self, event):
        """Salva a geometria da janela ao fechar"""
        self.salvar_geometria()
        super().closeEvent(event)
        
    def salvar_geometria(self):
        """Salva tamanho e posição da janela"""
        self.settings.setValue("tela_principal/geometry", self.saveGeometry())
        
    def restaurar_geometria(self):
        """Restaura tamanho e posição da janela"""
        geometry = self.settings.value("tela_principal/geometry")
        if geometry:
            self.restoreGeometry(geometry)
