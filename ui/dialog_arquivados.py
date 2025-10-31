"""
Dialog para Ver Alunos Arquivados (Formados)
Exibe alunos que foram marcados como "Formado(a)"
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from database import db
from ui.styles import aplicar_classe_botao, aplicar_classe_label
from utils.formatters import formatar_data_br, truncar_texto


class DialogArquivados(QDialog):
    """Dialog para visualizar alunos arquivados (formados)"""
    
    def __init__(self, unidade_id: int, parent=None):
        super().__init__(parent)
        self.unidade_id = unidade_id
        self.alunos = []
        
        self.init_ui()
        self.carregar_alunos()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("Alunos Arquivados (Formados)")
        self.setMinimumSize(900, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Alunos Formados")
        aplicar_classe_label(titulo, "subtitle")
        layout.addWidget(titulo)
        
        # Descrição
        descricao = QLabel(
            "Esta lista mostra os alunos que foram marcados como 'Formado(a)' "
            "e estão arquivados (não aparecem na lista principal)."
        )
        descricao.setWordWrap(True)
        aplicar_classe_label(descricao, "info")
        layout.addWidget(descricao)
        
        # Tabela de alunos arquivados
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Nome", "Curso", "Data Início", "Situação", "Instrutor", "Observações"
        ])
        
        # Configurações da tabela
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        
        # Ajustar colunas
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nome
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Curso
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Data Início
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Situação
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Instrutor
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Observações
        
        layout.addWidget(self.tabela)
        
        # Botões de ação
        layout_botoes = QHBoxLayout()
        
        btn_desarquivar = QPushButton("Desarquivar Selecionado")
        aplicar_classe_botao(btn_desarquivar, "success")
        btn_desarquivar.clicked.connect(self.desarquivar_aluno)
        layout_botoes.addWidget(btn_desarquivar)
        
        btn_atualizar = QPushButton("Atualizar Lista")
        btn_atualizar.clicked.connect(self.carregar_alunos)
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
        
    def carregar_alunos(self):
        """Carrega os alunos arquivados"""
        # Buscar todos os alunos (incluindo arquivados)
        todos_alunos = db.listar_alunos(self.unidade_id, incluir_arquivados=True)
        
        # Filtrar apenas os arquivados
        self.alunos = [a for a in todos_alunos if a.get('arquivado', False)]
        
        self.tabela.setRowCount(0)
        
        for aluno in self.alunos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # Nome
            item_nome = QTableWidgetItem(aluno['nome'])
            item_nome.setData(Qt.UserRole, aluno['id'])
            self.tabela.setItem(row, 0, item_nome)
            
            # Curso
            self.tabela.setItem(row, 1, QTableWidgetItem(aluno.get('curso_matriculado', '')))
            
            # Data de Início
            data_inicio = formatar_data_br(aluno.get('data_inicio'))
            self.tabela.setItem(row, 2, QTableWidgetItem(data_inicio))
            
            # Situação
            situacao = aluno.get('situacao_academica', '')
            item_situacao = QTableWidgetItem(situacao)
            item_situacao.setForeground(Qt.darkGray)
            self.tabela.setItem(row, 3, item_situacao)
            
            # Instrutor
            instrutor_nome = ""
            if aluno.get('instrutores'):
                instrutor_nome = aluno['instrutores'].get('nome', '')
            self.tabela.setItem(row, 4, QTableWidgetItem(instrutor_nome))
            
            # Observações (truncadas)
            obs = truncar_texto(aluno.get('observacoes', ''), 50)
            self.tabela.setItem(row, 5, QTableWidgetItem(obs))
        
        self.label_status.setText(f"Total de alunos arquivados: {len(self.alunos)}")
        
    def desarquivar_aluno(self):
        """Desarquiva o aluno selecionado (volta para a lista principal)"""
        linha_selecionada = self.tabela.currentRow()
        
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno")
            return
        
        aluno_id = self.tabela.item(linha_selecionada, 0).data(Qt.UserRole)
        aluno_nome = self.tabela.item(linha_selecionada, 0).text()
        
        # Confirmar
        resposta = QMessageBox.question(
            self,
            "Confirmar Desarquivamento",
            f"Deseja desarquivar o aluno '{aluno_nome}'?\n\n"
            "O aluno voltará a aparecer na lista principal.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            sucesso, mensagem = db.arquivar_aluno(aluno_id, arquivar=False)
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.carregar_alunos()
            else:
                QMessageBox.critical(self, "Erro", mensagem)
