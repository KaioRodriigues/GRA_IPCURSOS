"""
Tela de Seleção de Instrutor
Permite selecionar um instrutor ou gerenciar instrutores
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QMessageBox, QDialog, QLineEdit,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Signal, Qt, QSettings
from database import db
from ui.styles import aplicar_classe_label, aplicar_classe_botao


class DialogGerenciarInstrutores(QDialog):
    """Dialog para adicionar e excluir instrutores"""
    
    def __init__(self, unidade_id: int, unidade_nome: str, parent=None):
        super().__init__(parent)
        self.unidade_id = unidade_id
        self.unidade_nome = unidade_nome
        self.instrutores = []
        self.init_ui()
        self.carregar_instrutores()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle(f"Gerenciar Instrutores - {self.unidade_nome}")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Gerenciar Instrutores")
        aplicar_classe_label(titulo, "subtitle")
        layout.addWidget(titulo)
        
        # Seção: Adicionar Instrutor
        grupo_adicionar = QVBoxLayout()
        
        label_adicionar = QLabel("Adicionar Novo Instrutor:")
        grupo_adicionar.addWidget(label_adicionar)
        
        layout_adicionar = QHBoxLayout()
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome do instrutor")
        layout_adicionar.addWidget(self.input_nome)
        
        btn_adicionar = QPushButton("Adicionar")
        aplicar_classe_botao(btn_adicionar, "success")
        btn_adicionar.clicked.connect(self.adicionar_instrutor)
        layout_adicionar.addWidget(btn_adicionar)
        
        grupo_adicionar.addLayout(layout_adicionar)
        layout.addLayout(grupo_adicionar)
        
        # Seção: Lista de Instrutores
        label_lista = QLabel("Instrutores Cadastrados:")
        layout.addWidget(label_lista)
        
        self.lista_instrutores = QListWidget()
        layout.addWidget(self.lista_instrutores)
        
        # Botões de ação
        layout_botoes = QHBoxLayout()
        
        btn_excluir = QPushButton("Excluir Selecionado")
        aplicar_classe_botao(btn_excluir, "danger")
        btn_excluir.clicked.connect(self.excluir_instrutor)
        layout_botoes.addWidget(btn_excluir)
        
        btn_atualizar = QPushButton("Atualizar Lista")
        btn_atualizar.clicked.connect(self.carregar_instrutores)
        layout_botoes.addWidget(btn_atualizar)
        
        btn_fechar = QPushButton("Fechar")
        aplicar_classe_botao(btn_fechar, "secondary")
        btn_fechar.clicked.connect(self.accept)
        layout_botoes.addWidget(btn_fechar)
        
        layout.addLayout(layout_botoes)
        
        self.setLayout(layout)
        
    def carregar_instrutores(self):
        """Carrega a lista de instrutores"""
        self.lista_instrutores.clear()
        self.instrutores = db.listar_instrutores(self.unidade_id, apenas_ativos=False)
        
        for instrutor in self.instrutores:
            status = "✓ Ativo" if instrutor['ativo'] else "✗ Inativo"
            item = QListWidgetItem(f"{instrutor['nome']} - {status}")
            item.setData(Qt.UserRole, instrutor['id'])
            self.lista_instrutores.addItem(item)
            
    def adicionar_instrutor(self):
        """Adiciona um novo instrutor"""
        nome = self.input_nome.text().strip()
        
        if not nome:
            QMessageBox.warning(self, "Atenção", "Digite o nome do instrutor")
            return
        
        sucesso, mensagem = db.adicionar_instrutor(nome, self.unidade_id)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.input_nome.clear()
            self.carregar_instrutores()
            
            # Registrar log
            db.adicionar_log(
                instrutor_id=None,
                atividade=f"Adicionou instrutor: {nome}",
                unidade_id=self.unidade_id
            )
        else:
            QMessageBox.critical(self, "Erro", mensagem)
            
    def excluir_instrutor(self):
        """Exclui (marca como inativo) o instrutor selecionado"""
        item_atual = self.lista_instrutores.currentItem()
        
        if not item_atual:
            QMessageBox.warning(self, "Atenção", "Selecione um instrutor")
            return
        
        instrutor_id = item_atual.data(Qt.UserRole)
        
        # Buscar nome do instrutor
        instrutor = next((i for i in self.instrutores if i['id'] == instrutor_id), None)
        if not instrutor:
            return
        
        # Confirmar exclusão
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja realmente excluir o instrutor '{instrutor['nome']}'?\n\n"
            "Nota: O instrutor será marcado como inativo.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            sucesso, mensagem = db.excluir_instrutor(instrutor_id)
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.carregar_instrutores()
                
                # Registrar log
                db.adicionar_log(
                    instrutor_id=None,
                    atividade=f"Excluiu instrutor: {instrutor['nome']}",
                    unidade_id=self.unidade_id
                )
            else:
                QMessageBox.critical(self, "Erro", mensagem)


class TelaInstrutor(QWidget):
    """Tela para seleção de instrutor"""
    
    # Signal emitido quando um instrutor é selecionado
    instrutor_selecionado = Signal(int, str)  # (id, nome)
    
    def __init__(self, unidade_id: int, unidade_nome: str):
        super().__init__()
        self.unidade_id = unidade_id
        self.unidade_nome = unidade_nome
        self.instrutores = []
        self.settings = QSettings("SistemaGestao", "GestaoAlunos")
        self.init_ui()
        self.restaurar_geometria()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle(f"Seleção de Instrutor - {self.unidade_nome}")
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        titulo = QLabel(f"Unidade: {self.unidade_nome}")
        aplicar_classe_label(titulo, "title")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Selecione o Instrutor")
        aplicar_classe_label(subtitulo, "subtitle")
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)
        
        # Espaçador
        layout.addStretch()
        
        # ComboBox de instrutores
        label_instrutor = QLabel("Instrutor:")
        layout.addWidget(label_instrutor)
        
        self.combo_instrutor = QComboBox()
        self.combo_instrutor.setMinimumHeight(40)
        layout.addWidget(self.combo_instrutor)
        
        # Espaçador
        layout.addStretch()
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        btn_gerenciar = QPushButton("Gerenciar Instrutores")
        aplicar_classe_botao(btn_gerenciar, "secondary")
        btn_gerenciar.clicked.connect(self.abrir_gerenciar)
        layout_botoes.addWidget(btn_gerenciar)
        
        btn_entrar = QPushButton("Entrar")
        aplicar_classe_botao(btn_entrar, "success")
        btn_entrar.clicked.connect(self.entrar)
        layout_botoes.addWidget(btn_entrar)
        
        layout.addLayout(layout_botoes)
        
        self.setLayout(layout)
        
    def showEvent(self, event):
        """Evento chamado quando a janela é exibida"""
        super().showEvent(event)
        self.carregar_instrutores()
        
    def carregar_instrutores(self):
        """Carrega os instrutores no ComboBox"""
        self.combo_instrutor.clear()
        self.instrutores = db.listar_instrutores(self.unidade_id, apenas_ativos=True)
        
        if not self.instrutores:
            self.combo_instrutor.addItem("Nenhum instrutor cadastrado")
            return
        
        for instrutor in self.instrutores:
            self.combo_instrutor.addItem(instrutor['nome'], instrutor['id'])
            
    def abrir_gerenciar(self):
        """Abre o dialog de gerenciamento de instrutores"""
        dialog = DialogGerenciarInstrutores(self.unidade_id, self.unidade_nome, self)
        dialog.exec()
        
        # Recarregar lista após fechar o dialog
        self.carregar_instrutores()
        
    def entrar(self):
        """Seleciona o instrutor e avança para a tela principal"""
        if not self.instrutores:
            QMessageBox.warning(
                self,
                "Atenção",
                "Nenhum instrutor cadastrado. Por favor, cadastre um instrutor primeiro."
            )
            return
        
        instrutor_id = self.combo_instrutor.currentData()
        instrutor_nome = self.combo_instrutor.currentText()
        
        if instrutor_id:
            self.instrutor_selecionado.emit(instrutor_id, instrutor_nome)
            
    def closeEvent(self, event):
        """Salva a geometria da janela ao fechar"""
        self.salvar_geometria()
        super().closeEvent(event)
        
    def salvar_geometria(self):
        """Salva tamanho e posição da janela"""
        self.settings.setValue("tela_instrutor/geometry", self.saveGeometry())
        
    def restaurar_geometria(self):
        """Restaura tamanho e posição da janela"""
        geometry = self.settings.value("tela_instrutor/geometry")
        if geometry:
            self.restoreGeometry(geometry)
