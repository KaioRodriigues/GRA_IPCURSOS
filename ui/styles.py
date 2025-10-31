"""
Estilos e temas da aplicação
Define o visual moderno do sistema usando QSS (Qt Style Sheets)
"""

# ============================================
# TEMA PRINCIPAL - DESIGN MODERNO
# ============================================

ESTILO_PRINCIPAL = """
/* ========================================== */
/* CONFIGURAÇÕES GLOBAIS */
/* ========================================== */
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
    color: #2c3e50;
}

QMainWindow {
    background-color: #ecf0f1;
}

/* ========================================== */
/* BOTÕES */
/* ========================================== */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    min-height: 35px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

/* Botão de sucesso (verde) */
QPushButton[class="success"] {
    background-color: #27ae60;
}

QPushButton[class="success"]:hover {
    background-color: #229954;
}

/* Botão de perigo (vermelho) */
QPushButton[class="danger"] {
    background-color: #e74c3c;
}

QPushButton[class="danger"]:hover {
    background-color: #c0392b;
}

/* Botão secundário (cinza) */
QPushButton[class="secondary"] {
    background-color: #95a5a6;
}

QPushButton[class="secondary"]:hover {
    background-color: #7f8c8d;
}

/* ========================================== */
/* CAMPOS DE ENTRADA */
/* ========================================== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: white;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #3498db;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #3498db;
}

QLineEdit:disabled, QTextEdit:disabled {
    background-color: #ecf0f1;
    color: #7f8c8d;
}

/* ========================================== */
/* COMBOBOX (DROPDOWN) */
/* ========================================== */
QComboBox {
    background-color: white;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    padding: 8px;
    min-height: 35px;
}

QComboBox:hover {
    border: 2px solid #3498db;
}

QComboBox:focus {
    border: 2px solid #3498db;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #2c3e50;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: white;
    border: 2px solid #3498db;
    selection-background-color: #3498db;
    selection-color: white;
    outline: none;
}

/* ========================================== */
/* TABELAS */
/* ========================================== */
QTableWidget {
    background-color: white;
    alternate-background-color: #f8f9fa;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    gridline-color: #ecf0f1;
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QTableWidget::item:hover {
    background-color: #d6eaf8;
}

QHeaderView::section {
    background-color: #34495e;
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
    border-right: 1px solid #2c3e50;
}

QHeaderView::section:hover {
    background-color: #2c3e50;
}

/* ========================================== */
/* LABELS */
/* ========================================== */
QLabel {
    color: #2c3e50;
}

QLabel[class="title"] {
    font-size: 24pt;
    font-weight: bold;
    color: #2c3e50;
    padding: 10px 0;
}

QLabel[class="subtitle"] {
    font-size: 14pt;
    font-weight: bold;
    color: #34495e;
    padding: 5px 0;
}

QLabel[class="info"] {
    color: #7f8c8d;
    font-size: 9pt;
}

/* ========================================== */
/* GROUPBOX */
/* ========================================== */
QGroupBox {
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 10px;
    color: #2c3e50;
}

/* ========================================== */
/* SCROLLBAR */
/* ========================================== */
QScrollBar:vertical {
    background-color: #ecf0f1;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #95a5a6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #ecf0f1;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #95a5a6;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========================================== */
/* DIALOGS */
/* ========================================== */
QDialog {
    background-color: #ecf0f1;
}

/* ========================================== */
/* CHECKBOX E RADIOBUTTON */
/* ========================================== */
QCheckBox, QRadioButton {
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 20px;
    height: 20px;
}

QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
    border: 2px solid #bdc3c7;
    background-color: white;
    border-radius: 4px;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    border: 2px solid #3498db;
    background-color: #3498db;
    border-radius: 4px;
}

/* ========================================== */
/* MENSAGENS DE STATUS */
/* ========================================== */
QStatusBar {
    background-color: #34495e;
    color: white;
}

QStatusBar::item {
    border: none;
}
"""

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def aplicar_classe_botao(botao, classe: str):
    """
    Aplica uma classe CSS a um botão
    
    Args:
        botao: QPushButton
        classe: Nome da classe (success, danger, secondary)
    """
    botao.setProperty("class", classe)
    botao.style().unpolish(botao)
    botao.style().polish(botao)


def aplicar_classe_label(label, classe: str):
    """
    Aplica uma classe CSS a um label
    
    Args:
        label: QLabel
        classe: Nome da classe (title, subtitle, info)
    """
    label.setProperty("class", classe)
    label.style().unpolish(label)
    label.style().polish(label)
