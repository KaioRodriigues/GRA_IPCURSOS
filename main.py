"""
Sistema de Gestão de Alunos
Aplicação principal que gerencia o fluxo entre as telas
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QInputDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import QSettings
from config import Config
from database import db
from ui.styles import ESTILO_PRINCIPAL, aplicar_classe_botao
from ui.tela_unidade import TelaUnidade
from ui.tela_instrutor import TelaInstrutor
from ui.tela_principal import TelaPrincipal


class DialogConfigurarSupabase(QDialog):
    """Dialog para configurar as credenciais do Supabase"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("Configurar Supabase")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Configuração do Supabase")
        titulo.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(titulo)
        
        # Descrição
        descricao = QLabel(
            "Para usar este sistema, você precisa configurar as credenciais do Supabase.\n\n"
            "Você pode encontrar essas informações no painel do seu projeto Supabase:\n"
            "Settings → API → Project URL e Project API keys (anon/public)"
        )
        descricao.setWordWrap(True)
        layout.addWidget(descricao)
        
        # Campo URL
        label_url = QLabel("URL do Projeto Supabase:")
        layout.addWidget(label_url)
        
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://seu-projeto.supabase.co")
        self.input_url.setText(Config.SUPABASE_URL)
        layout.addWidget(self.input_url)
        
        # Campo Key
        label_key = QLabel("Chave Anônima (anon key):")
        layout.addWidget(label_key)
        
        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        self.input_key.setText(Config.SUPABASE_KEY)
        layout.addWidget(self.input_key)
        
        # Nota
        nota = QLabel(
            "Nota: As credenciais serão salvas localmente no arquivo .env"
        )
        nota.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        layout.addWidget(nota)
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        aplicar_classe_botao(btn_cancelar, "secondary")
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)
        
        btn_salvar = QPushButton("Salvar e Conectar")
        aplicar_classe_botao(btn_salvar, "success")
        btn_salvar.clicked.connect(self.salvar)
        layout_botoes.addWidget(btn_salvar)
        
        layout.addLayout(layout_botoes)
        
        self.setLayout(layout)
        
    def salvar(self):
        """Salva as credenciais"""
        url = self.input_url.text().strip()
        key = self.input_key.text().strip()
        
        if not url or not key:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos")
            return
        
        if not url.startswith("https://"):
            QMessageBox.warning(self, "Atenção", "A URL deve começar com https://")
            return
        
        # Configurar
        Config.configurar_credenciais(url, key)
        
        self.accept()


class AplicacaoGestaoAlunos:
    """Classe principal da aplicação"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(Config.APP_NAME)
        self.app.setOrganizationName(Config.ORGANIZATION)
        
        # Aplicar estilo
        self.app.setStyleSheet(ESTILO_PRINCIPAL)
        
        # Janelas
        self.tela_unidade = None
        self.tela_instrutor = None
        self.tela_principal = None
        
        # Dados da sessão
        self.unidade_id = None
        self.unidade_nome = None
        self.instrutor_id = None
        self.instrutor_nome = None
        
    def iniciar(self):
        """Inicia a aplicação"""
        # Verificar e configurar credenciais do Supabase
        valido, mensagem = Config.validar_credenciais()
        
        if not valido:
            dialog = DialogConfigurarSupabase()
            if dialog.exec() != QDialog.Accepted:
                QMessageBox.critical(
                    None,
                    "Erro",
                    "Não é possível iniciar o sistema sem configurar o Supabase."
                )
                return 1
        
        # Conectar ao banco de dados
        sucesso, mensagem = db.conectar()
        if not sucesso:
            QMessageBox.critical(
                None,
                "Erro de Conexão",
                f"Não foi possível conectar ao Supabase:\n\n{mensagem}\n\n"
                "Verifique suas credenciais e tente novamente."
            )
            
            # Permitir reconfigurar
            dialog = DialogConfigurarSupabase()
            if dialog.exec() == QDialog.Accepted:
                sucesso, mensagem = db.conectar()
                if not sucesso:
                    QMessageBox.critical(None, "Erro", f"Ainda não foi possível conectar:\n\n{mensagem}")
                    return 1
            else:
                return 1
        
        # Mostrar tela de seleção de unidade
        self.mostrar_tela_unidade()
        
        return self.app.exec()
        
    def mostrar_tela_unidade(self):
        """Exibe a tela de seleção de unidade"""
        self.tela_unidade = TelaUnidade()
        self.tela_unidade.unidade_selecionada.connect(self.ao_selecionar_unidade)
        self.tela_unidade.show()
        
    def ao_selecionar_unidade(self, unidade_id: int, unidade_nome: str):
        """Callback quando uma unidade é selecionada"""
        self.unidade_id = unidade_id
        self.unidade_nome = unidade_nome
        
        # Fechar tela de unidade
        if self.tela_unidade:
            self.tela_unidade.close()
        
        # Mostrar tela de seleção de instrutor
        self.mostrar_tela_instrutor()
        
    def mostrar_tela_instrutor(self):
        """Exibe a tela de seleção de instrutor"""
        self.tela_instrutor = TelaInstrutor(self.unidade_id, self.unidade_nome)
        self.tela_instrutor.instrutor_selecionado.connect(self.ao_selecionar_instrutor)
        self.tela_instrutor.show()
        
    def ao_selecionar_instrutor(self, instrutor_id: int, instrutor_nome: str):
        """Callback quando um instrutor é selecionado"""
        self.instrutor_id = instrutor_id
        self.instrutor_nome = instrutor_nome
        
        # Registrar log de login
        db.adicionar_log(
            instrutor_id=self.instrutor_id,
            atividade=f"Login no sistema",
            unidade_id=self.unidade_id
        )
        
        # Fechar tela de instrutor
        if self.tela_instrutor:
            self.tela_instrutor.close()
        
        # Mostrar tela principal
        self.mostrar_tela_principal()
        
    def mostrar_tela_principal(self):
        """Exibe a tela principal"""
        self.tela_principal = TelaPrincipal(
            self.unidade_id,
            self.unidade_nome,
            self.instrutor_id,
            self.instrutor_nome
        )
        self.tela_principal.show()


def main():
    """Função principal"""
    app = AplicacaoGestaoAlunos()
    sys.exit(app.iniciar())


if __name__ == "__main__":
    main()
