"""
Dialog para Adicionar e Editar Alunos
Formulário completo com todos os campos necessários
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit,
    QMessageBox, QGroupBox, QCheckBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from datetime import datetime
import json

from database import db
from config import (
    TIPOS_PLANO, SITUACOES_ACADEMICAS, DIAS_SEMANA,
    OPCOES_AULAS, OPCOES_PAGAMENTO
)
from utils.validators import validar_data_br, validar_nome, auto_formatar_data
from utils.formatters import formatar_data_br
from ui.styles import aplicar_classe_botao


class DialogDiaHorario(QDialog):
    """Dialog para configurar dias e horários"""
    
    def __init__(self, dados_iniciais: dict = None, parent=None):
        super().__init__(parent)
        self.dados_iniciais = dados_iniciais or {}
        self.horarios_por_dia = {}  # {dia: [horario1, horario2, ...]}
        self.init_ui()
        self.carregar_dados_iniciais()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("Configurar Dias e Horários")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("Configure os dias e horários das aulas:")
        layout.addWidget(titulo)
        
        # Criar seção para cada dia
        form = QFormLayout()
        
        for dia in DIAS_SEMANA:
            layout_dia = QVBoxLayout()
            
            # Lista de horários do dia
            lista_horarios = QListWidget()
            lista_horarios.setMaximumHeight(80)
            layout_dia.addWidget(lista_horarios)
            
            # Botões de ação
            layout_botoes_dia = QHBoxLayout()
            
            input_horario = QLineEdit()
            input_horario.setPlaceholderText("Ex: 20:00 ou 20")
            layout_botoes_dia.addWidget(input_horario)
            
            btn_adicionar = QPushButton("Adicionar")
            btn_adicionar.clicked.connect(
                lambda checked, d=dia, inp=input_horario, lst=lista_horarios: 
                self.adicionar_horario(d, inp, lst)
            )
            layout_botoes_dia.addWidget(btn_adicionar)
            
            btn_remover = QPushButton("Remover")
            btn_remover.clicked.connect(
                lambda checked, d=dia, lst=lista_horarios: 
                self.remover_horario(d, lst)
            )
            layout_botoes_dia.addWidget(btn_remover)
            
            layout_dia.addLayout(layout_botoes_dia)
            
            form.addRow(f"{dia}:", layout_dia)
            
            self.horarios_por_dia[dia] = {
                'lista': lista_horarios,
                'input': input_horario,
                'horarios': []
            }
        
        layout.addLayout(form)
        
        # Informação
        info = QLabel("Dica: Digite apenas a hora (ex: 20) que será formatado automaticamente para 20:00. Você pode adicionar vários horários por dia.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        layout.addWidget(info)
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        aplicar_classe_botao(btn_cancelar, "secondary")
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)
        
        btn_confirmar = QPushButton("Confirmar")
        aplicar_classe_botao(btn_confirmar, "success")
        btn_confirmar.clicked.connect(self.confirmar)
        layout_botoes.addWidget(btn_confirmar)
        
        layout.addLayout(layout_botoes)
        
        self.setLayout(layout)
        
    def carregar_dados_iniciais(self):
        """Carrega os dados iniciais na interface"""
        for dia, dados in self.dados_iniciais.items():
            if dia in self.horarios_por_dia:
                # Suporta tanto string única quanto lista de horários
                if isinstance(dados, str):
                    horarios = [dados]
                elif isinstance(dados, list):
                    horarios = dados
                else:
                    continue
                
                for horario in horarios:
                    self.horarios_por_dia[dia]['horarios'].append(horario)
                    self.horarios_por_dia[dia]['lista'].addItem(horario)
    
    def adicionar_horario(self, dia: str, input_field: QLineEdit, lista: QListWidget):
        """Adiciona um horário à lista do dia"""
        horario = input_field.text().strip()
        
        if not horario:
            QMessageBox.warning(self, "Atenção", "Digite um horário")
            return
        
        # Auto-formatar: se é só número, adiciona :00
        if horario.isdigit():
            horario = f"{horario.zfill(2)}:00"
        
        # Validar formato básico
        if ':' not in horario:
            QMessageBox.warning(self, "Atenção", "Formato inválido. Use HH:MM")
            return
        
        # Adicionar à lista
        self.horarios_por_dia[dia]['horarios'].append(horario)
        lista.addItem(horario)
        input_field.clear()
    
    def remover_horario(self, dia: str, lista: QListWidget):
        """Remove o horário selecionado da lista"""
        item_atual = lista.currentItem()
        
        if not item_atual:
            QMessageBox.warning(self, "Atenção", "Selecione um horário para remover")
            return
        
        horario = item_atual.text()
        row = lista.currentRow()
        
        # Remover da lista visual
        lista.takeItem(row)
        
        # Remover dos dados
        if horario in self.horarios_por_dia[dia]['horarios']:
            self.horarios_por_dia[dia]['horarios'].remove(horario)
        
    def confirmar(self):
        """Valida e confirma os dados"""
        self.accept()
        
    def obter_dados(self) -> dict:
        """Retorna os dados configurados"""
        dados = {}
        for dia, info in self.horarios_por_dia.items():
            if info['horarios']:
                # Se houver apenas um horário, salvar como string para compatibilidade
                if len(info['horarios']) == 1:
                    dados[dia] = info['horarios'][0]
                else:
                    # Se houver múltiplos horários, salvar como lista
                    dados[dia] = info['horarios']
        return dados


class DialogAluno(QDialog):
    """Dialog para adicionar ou editar aluno"""
    
    def __init__(self, unidade_id: int, instrutor_id: int, aluno_id: int = None, parent=None):
        super().__init__(parent)
        self.unidade_id = unidade_id
        self.instrutor_id = instrutor_id
        self.aluno_id = aluno_id
        self.modo_edicao = aluno_id is not None
        self.dia_horario_dados = {}
        
        self.init_ui()
        
        if self.modo_edicao:
            self.carregar_dados_aluno()
            
    def init_ui(self):
        """Inicializa a interface"""
        titulo = "Editar Aluno" if self.modo_edicao else "Adicionar Aluno"
        self.setWindowTitle(titulo)
        self.setMinimumSize(600, 700)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(label_titulo)
        
        # Formulário
        form = QFormLayout()
        form.setSpacing(10)
        
        # Nome
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome completo do aluno")
        form.addRow("Nome:*", self.input_nome)
        
        # Data de Início
        self.input_data_inicio = QLineEdit()
        self.input_data_inicio.setPlaceholderText("DD/MM/AAAA")
        self.input_data_inicio.textChanged.connect(self.formatar_data_automaticamente)
        form.addRow("Data de Início:*", self.input_data_inicio)
        
        # Curso Matriculado
        self.input_curso = QLineEdit()
        self.input_curso.setPlaceholderText("Nome do curso")
        form.addRow("Curso Matriculado:*", self.input_curso)
        
        # Tipo de Plano
        self.combo_tipo_plano = QComboBox()
        self.combo_tipo_plano.addItems(TIPOS_PLANO)
        form.addRow("Tipo de Plano:*", self.combo_tipo_plano)
        
        # Módulo
        self.input_modulo = QLineEdit()
        self.input_modulo.setPlaceholderText("Ex: Módulo 1, Módulo Básico, etc.")
        form.addRow("Módulo:", self.input_modulo)
        
        # Aulas
        self.combo_aulas = QComboBox()
        self.combo_aulas.addItems(OPCOES_AULAS)
        form.addRow("Aulas:", self.combo_aulas)
        
        # Dia e Horário
        layout_dia_horario = QHBoxLayout()
        self.label_dia_horario = QLabel("Nenhum horário configurado")
        self.label_dia_horario.setStyleSheet("color: #7f8c8d;")
        layout_dia_horario.addWidget(self.label_dia_horario)
        
        btn_configurar_horario = QPushButton("Configurar")
        btn_configurar_horario.clicked.connect(self.abrir_dialog_horario)
        layout_dia_horario.addWidget(btn_configurar_horario)
        
        form.addRow("Dia e Horário:", layout_dia_horario)
        
        # Situação Acadêmica
        self.combo_situacao = QComboBox()
        self.combo_situacao.addItems(SITUACOES_ACADEMICAS)
        form.addRow("Situação Acadêmica:*", self.combo_situacao)
        
        # Observações
        self.input_observacoes = QTextEdit()
        self.input_observacoes.setPlaceholderText("Observações sobre o aluno")
        self.input_observacoes.setMaximumHeight(100)
        form.addRow("Observações:", self.input_observacoes)
        
        # Pagamento/Parcelas
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(OPCOES_PAGAMENTO)
        form.addRow("Pagamento/Parcelas:", self.combo_pagamento)
        
        layout.addLayout(form)
        
        # Nota sobre campos obrigatórios
        nota = QLabel("* Campos obrigatórios")
        nota.setStyleSheet("color: #e74c3c; font-size: 9pt;")
        layout.addWidget(nota)
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        aplicar_classe_botao(btn_cancelar, "secondary")
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)
        
        btn_salvar = QPushButton("Salvar")
        aplicar_classe_botao(btn_salvar, "success")
        btn_salvar.clicked.connect(self.salvar)
        layout_botoes.addWidget(btn_salvar)
        
        layout.addLayout(layout_botoes)
        
        self.setLayout(layout)
        
    def formatar_data_automaticamente(self, texto: str):
        """Formata a data automaticamente enquanto o usuário digita"""
        # Salvar posição do cursor
        cursor_pos = self.input_data_inicio.cursorPosition()
        
        # Formatar
        texto_formatado = auto_formatar_data(texto)
        
        # Atualizar campo se mudou
        if texto_formatado != texto:
            self.input_data_inicio.setText(texto_formatado)
            # Ajustar cursor
            self.input_data_inicio.setCursorPosition(min(cursor_pos + 1, len(texto_formatado)))
            
    def abrir_dialog_horario(self):
        """Abre o dialog para configurar dias e horários"""
        dialog = DialogDiaHorario(self.dia_horario_dados, self)
        if dialog.exec() == QDialog.Accepted:
            self.dia_horario_dados = dialog.obter_dados()
            self.atualizar_label_horario()
            
    def atualizar_label_horario(self):
        """Atualiza o label que mostra os horários configurados"""
        if not self.dia_horario_dados:
            self.label_dia_horario.setText("Nenhum horário configurado")
            return
        
        # Abreviações
        abrev = {
            "Segunda": "Seg", "Terça": "Ter", "Quarta": "Qua",
            "Quinta": "Qui", "Sexta": "Sex", "Sábado": "Sáb", "Domingo": "Dom"
        }
        
        resultado = []
        for dia, horario in self.dia_horario_dados.items():
            dia_abrev = abrev.get(dia, dia[:3])
            # Se for lista de horários, juntar com /
            if isinstance(horario, list):
                horarios_str = "/".join(horario)
                resultado.append(f"{dia_abrev} {horarios_str}")
            else:
                resultado.append(f"{dia_abrev} {horario}")
        
        self.label_dia_horario.setText(", ".join(resultado))
        
    def carregar_dados_aluno(self):
        """Carrega os dados do aluno para edição"""
        aluno = db.obter_aluno(self.aluno_id)
        if not aluno:
            QMessageBox.critical(self, "Erro", "Aluno não encontrado")
            self.reject()
            return
        
        # Preencher campos
        self.input_nome.setText(aluno.get('nome', ''))
        
        # Data de início
        if aluno.get('data_inicio'):
            self.input_data_inicio.setText(formatar_data_br(aluno['data_inicio']))
        
        self.input_curso.setText(aluno.get('curso_matriculado', ''))
        
        # Tipo de plano
        tipo_plano = aluno.get('tipo_plano', '')
        if tipo_plano in TIPOS_PLANO:
            self.combo_tipo_plano.setCurrentText(tipo_plano)
        
        self.input_modulo.setText(aluno.get('modulo', ''))
        
        # Aulas
        aulas = str(aluno.get('aulas', ''))
        if aulas in OPCOES_AULAS:
            self.combo_aulas.setCurrentText(aulas)
        
        # Dia e horário
        dia_horario = aluno.get('dia_horario')
        if dia_horario:
            if isinstance(dia_horario, str):
                try:
                    self.dia_horario_dados = json.loads(dia_horario)
                except:
                    self.dia_horario_dados = {}
            elif isinstance(dia_horario, dict):
                self.dia_horario_dados = dia_horario
            self.atualizar_label_horario()
        
        # Situação acadêmica
        situacao = aluno.get('situacao_academica', '')
        if situacao in SITUACOES_ACADEMICAS:
            self.combo_situacao.setCurrentText(situacao)
        
        self.input_observacoes.setPlainText(aluno.get('observacoes', ''))
        
        # Pagamento
        pagamento = str(aluno.get('pagamento_parcelas', ''))
        if pagamento in OPCOES_PAGAMENTO:
            self.combo_pagamento.setCurrentText(pagamento)
            
    def validar_campos(self) -> tuple[bool, str]:
        """Valida todos os campos do formulário"""
        # Nome
        nome = self.input_nome.text().strip()
        valido, mensagem = validar_nome(nome)
        if not valido:
            return False, mensagem
        
        # Data de início
        data_str = self.input_data_inicio.text().strip()
        valido, data = validar_data_br(data_str)
        if not valido:
            return False, "Data de início inválida. Use o formato DD/MM/AAAA"
        
        # Curso
        curso = self.input_curso.text().strip()
        if not curso:
            return False, "Curso matriculado é obrigatório"
        
        return True, ""
        
    def salvar(self):
        """Salva os dados do aluno"""
        # Validar
        valido, mensagem = self.validar_campos()
        if not valido:
            QMessageBox.warning(self, "Validação", mensagem)
            return
        
        # Coletar dados
        data_str = self.input_data_inicio.text().strip()
        _, data_obj = validar_data_br(data_str)
        
        dados = {
            'nome': self.input_nome.text().strip(),
            'data_inicio': data_obj.date(),
            'curso_matriculado': self.input_curso.text().strip(),
            'tipo_plano': self.combo_tipo_plano.currentText(),
            'modulo': self.input_modulo.text().strip(),
            'aulas': int(self.combo_aulas.currentText()) if self.combo_aulas.currentText().isdigit() else None,
            'dia_horario': self.dia_horario_dados,
            'situacao_academica': self.combo_situacao.currentText(),
            'observacoes': self.input_observacoes.toPlainText().strip(),
            'pagamento_parcelas': self.combo_pagamento.currentText(),
            'instrutor_id': self.instrutor_id,
            'unidade_id': self.unidade_id
        }
        
        # Salvar no banco
        if self.modo_edicao:
            sucesso, mensagem = db.atualizar_aluno(self.aluno_id, dados)
            acao_log = f"Editou aluno: {dados['nome']}"
        else:
            sucesso, mensagem = db.adicionar_aluno(dados)
            acao_log = f"Adicionou aluno: {dados['nome']}"
        
        if sucesso:
            # Registrar log
            db.adicionar_log(
                instrutor_id=self.instrutor_id,
                atividade=acao_log,
                unidade_id=self.unidade_id
            )
            
            QMessageBox.information(self, "Sucesso", mensagem)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", mensagem)
