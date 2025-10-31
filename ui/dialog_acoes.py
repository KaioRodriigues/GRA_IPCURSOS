"""
Dialog para Gerenciar Ações
Permite visualizar, adicionar e concluir ações de um aluno
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLineEdit, QAbstractItemView
)
from PySide6.QtCore import Qt
from database import db
from ui.styles import aplicar_classe_botao, aplicar_classe_label
from utils.formatters import formatar_data_br


class DialogAcoes(QDialog):
    """Dialog para gerenciar ações de um aluno"""
    
    def __init__(self, aluno_id: int, aluno_nome: str, instrutor_id: int, unidade_id: int, parent=None):
        super().__init__(parent)
        self.aluno_id = aluno_id
        self.aluno_nome = aluno_nome
        self.instrutor_id = instrutor_id
        self.unidade_id = unidade_id
        self.acoes = []
        
        self.init_ui()
        self.carregar_acoes()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle(f"Gerenciar Ações - {self.aluno_nome}")
        self.setMinimumSize(800, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel(f"Ações do Aluno: {self.aluno_nome}")
        aplicar_classe_label(titulo, "subtitle")
        layout.addWidget(titulo)
        
        # Tabela de ações
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels([
            "Ação Proposta", "Status", "Instrutor Resp.", "Data Proposta", "Data Conclusão"
        ])
        
        # Configurações da tabela
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        
        # Ajustar colunas
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Ação Proposta
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Instrutor
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Data Proposta
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Data Conclusão
        
        layout.addWidget(self.tabela)
        
        # Seção: Nova Ação
        layout_nova_acao = QVBoxLayout()
        
        label_nova = QLabel("Nova Ação:")
        layout_nova_acao.addWidget(label_nova)
        
        layout_input = QHBoxLayout()
        
        self.input_nova_acao = QLineEdit()
        self.input_nova_acao.setPlaceholderText("Digite a ação proposta...")
        layout_input.addWidget(self.input_nova_acao)
        
        btn_propor = QPushButton("Propor Ação")
        aplicar_classe_botao(btn_propor, "success")
        btn_propor.clicked.connect(self.propor_acao)
        layout_input.addWidget(btn_propor)
        
        layout_nova_acao.addLayout(layout_input)
        layout.addLayout(layout_nova_acao)
        
        # Botões de ação
        layout_botoes = QHBoxLayout()
        
        btn_concluir = QPushButton("Marcar Ação Selecionada como Concluída")
        aplicar_classe_botao(btn_concluir, "success")
        btn_concluir.clicked.connect(self.concluir_acao)
        layout_botoes.addWidget(btn_concluir)
        
        btn_atualizar = QPushButton("Atualizar Lista")
        btn_atualizar.clicked.connect(self.carregar_acoes)
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
        
    def carregar_acoes(self):
        """Carrega as ações do aluno"""
        self.acoes = db.listar_acoes(self.aluno_id)
        
        self.tabela.setRowCount(0)
        
        for acao in self.acoes:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # Ação Proposta
            item_acao = QTableWidgetItem(acao['acao_proposta'])
            item_acao.setData(Qt.UserRole, acao['id'])
            self.tabela.setItem(row, 0, item_acao)
            
            # Status
            status = acao.get('status', 'Pendente')
            item_status = QTableWidgetItem(status)
            
            # Colorir status
            if status == "Pendente":
                item_status.setForeground(Qt.red)
            elif status == "Concluída":
                item_status.setForeground(Qt.darkGreen)
            
            self.tabela.setItem(row, 1, item_status)
            
            # Instrutor Responsável
            instrutor_nome = ""
            if acao.get('instrutores'):
                instrutor_nome = acao['instrutores'].get('nome', '')
            self.tabela.setItem(row, 2, QTableWidgetItem(instrutor_nome))
            
            # Data Proposta
            data_proposta = formatar_data_br(acao.get('data_proposta'))
            self.tabela.setItem(row, 3, QTableWidgetItem(data_proposta))
            
            # Data Conclusão
            data_conclusao = formatar_data_br(acao.get('data_conclusao'))
            self.tabela.setItem(row, 4, QTableWidgetItem(data_conclusao))
        
        # Contar ações pendentes
        pendentes = sum(1 for a in self.acoes if a.get('status') == 'Pendente')
        concluidas = sum(1 for a in self.acoes if a.get('status') == 'Concluída')
        
        self.label_status.setText(
            f"Total: {len(self.acoes)} ação(ões) | "
            f"Pendentes: {pendentes} | Concluídas: {concluidas}"
        )
        
    def propor_acao(self):
        """Propõe uma nova ação"""
        acao_texto = self.input_nova_acao.text().strip()
        
        if not acao_texto:
            QMessageBox.warning(self, "Atenção", "Digite a ação proposta")
            return
        
        sucesso, mensagem = db.adicionar_acao(
            self.aluno_id,
            acao_texto,
            self.instrutor_id
        )
        
        if sucesso:
            # Registrar log
            db.adicionar_log(
                instrutor_id=self.instrutor_id,
                atividade=f"Propôs ação para {self.aluno_nome}: {acao_texto}",
                unidade_id=self.unidade_id
            )
            
            QMessageBox.information(self, "Sucesso", mensagem)
            self.input_nova_acao.clear()
            self.carregar_acoes()
        else:
            QMessageBox.critical(self, "Erro", mensagem)
            
    def concluir_acao(self):
        """Marca a ação selecionada como concluída"""
        linha_selecionada = self.tabela.currentRow()
        
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma ação")
            return
        
        acao_id = self.tabela.item(linha_selecionada, 0).data(Qt.UserRole)
        acao_texto = self.tabela.item(linha_selecionada, 0).text()
        status_atual = self.tabela.item(linha_selecionada, 1).text()
        
        # Verificar se já está concluída
        if status_atual == "Concluída":
            QMessageBox.information(self, "Informação", "Esta ação já está concluída")
            return
        
        # Confirmar
        resposta = QMessageBox.question(
            self,
            "Confirmar Conclusão",
            f"Marcar como concluída a ação:\n\n{acao_texto}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            sucesso, mensagem = db.concluir_acao(acao_id)
            
            if sucesso:
                # Registrar log
                db.adicionar_log(
                    instrutor_id=self.instrutor_id,
                    atividade=f"Concluiu ação para {self.aluno_nome}: {acao_texto}",
                    unidade_id=self.unidade_id
                )
                
                QMessageBox.information(self, "Sucesso", mensagem)
                self.carregar_acoes()
            else:
                QMessageBox.critical(self, "Erro", mensagem)
