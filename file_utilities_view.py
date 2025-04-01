"""Módulo para geração de interfaces gráficas."""

# -----------------------------------------------------------------------------

# CONCEITOS GERAIS:
# Manter régua de limite em 80 caracteres por linha.
# Nomes em Inglês, abreviados sempre que possível, para manter a régua.
# Documentaçao (Comentários, anotações e 'docstrings') em Português-Br.

# -----------------------------------------------------------------------------
# 01 => IMPORTACOES DE MODULOS

import sys
import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import PyQt5.QtGui as QtG

# -----------------------------------------------------------------------------
# 02 => INTERFACE PRINCIPAL


class MainUserInterface(QtW.QMainWindow):
    def __init__(self, name):
        super().__init__()
        self.setWindowTitle(name)
        self.setFixedSize(640, 490)
        self.input_dict = {}
        self.setCentralWidget(self.__central_widget("central_widget", self))
        self.setMenuBar(self.__menubar(self))
        self.setFont(font())

    def __central_widget(self, name: str, parent: QtW.QWidget) -> QtW.QWidget:
        central_widget = QtW.QWidget(parent)
        central_widget.setObjectName(name)
        central_widget.setFixedSize(640, 465)
        central_widget.setLayout(self.__main_layout("main_layout"))
        return central_widget

    def __main_layout(self, name: str) -> QtW.QVBoxLayout:
        layout = QtW.QVBoxLayout()
        layout.setObjectName(name)
        layout.setSpacing(2)
        layout.addLayout(self.__first_layout("first_layout"))
        layout.addLayout(self.__second_layout("second_layout"))
        layout.addWidget(
            self.__terminal_widget("terminal"), alignment=QtC.Qt.AlignHCenter
        )
        return layout

    def __first_layout(self, name: str) -> QtW.QHBoxLayout:
        layout = QtW.QHBoxLayout()
        layout.setObjectName(name)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__selectors_group("selectors_group"))
        layout.addWidget(
            self.__actions_group("actions"), alignment=QtC.Qt.AlignTop
        )
        return layout

    def __second_layout(self, name: str) -> QtW.QHBoxLayout:
        layout = QtW.QHBoxLayout()
        layout.setObjectName(name)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(
            self.__input_group(
                name="code_column",
                text="Coluna com Códigos",
            )
        )
        layout.addWidget(
            self.__input_group(
                name="keyword_column",
                text="Coluna com Palavra-Chave",
            )
        )
        layout.addWidget(
            self.__input_group(
                name="keyword_list",
                text="Lista de Palavras-Chave",
            )
        )
        layout.setAlignment(QtC.Qt.AlignCenter)
        return layout

    def __terminal_widget(self, name: str) -> QtW.QPlainTextEdit:
        terminal = QtW.QPlainTextEdit()
        terminal.setObjectName(name)
        terminal.setFixedSize(620, 130)
        terminal.setReadOnly(True)
        return terminal

    def __selectors_group(self, name: str) -> QtW.QGroupBox:
        group = QtW.QGroupBox()
        group.setObjectName(name)
        group.setFixedSize(470, 230)
        group.setContentsMargins(0, 0, 0, 0)
        group.setLayout(self.__selectors_layout("selectors_layout"))
        return group

    def __selectors_layout(self, name: str) -> QtW.QVBoxLayout:
        layout = QtW.QVBoxLayout()
        layout.setObjectName(name)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtC.Qt.AlignCenter)
        layout.addWidget(
            self.__selector_subgroup(
                name="table",
                text="Arquivo com tabela",
            )
        )
        layout.addWidget(
            self.__selector_subgroup(
                name="source",
                text="Local com arquivos-fonte",
            )
        )
        layout.addWidget(
            self.__selector_subgroup(
                name="target",
                text="Local-alvo para as pastas criadas",
            )
        )
        return layout

    def __selector_subgroup(self, name: str, text: str) -> QtW.QGroupBox:
        group = QtW.QGroupBox()
        group.setObjectName(f"{name}_group")
        group.setFixedSize(460, 70)
        group.setContentsMargins(0, 0, 0, 0)
        group.setLayout(self.__selector_sublayout(name, text))
        return group

    def __selector_sublayout(
        self: str, name: str, text: str
    ) -> QtW.QGridLayout:
        """Retorna layout-padrão de seletor.

        Constrói e retorna layout contendo 3 widgets: QLabel, QLineEdit
        e QPushButton. Adiciona o par QPushButton:QLineEdit ao dicionário.

        :param name: Nome base para os objetos criados.
        :type name: str
        :param text: Texto apresentado no widget QLabel.
        :type text: str
        :returns layout: Objeto QGridLayout
        :rtype: QtW.QGridLayout
        """
        layout = QtW.QGridLayout()
        layout.addWidget(self.__label(name, text, (440, 16)), 0, 0)
        layout.addWidget(self.__button(name, "Procurar", (90, 25)), 1, 1)
        layout.addWidget(self.__line_edit(name, (340, 25)), 1, 0)
        layout.setObjectName(f"{name}_layout")
        return layout

    def __actions_group(self, name: str) -> QtW.QGroupBox:
        # Grupo com botões de ação
        group = QtW.QGroupBox()
        group.setObjectName(f"{name}_group")
        group.setFixedSize(140, 200)
        group.setContentsMargins(0, 0, 0, 0)
        group.setLayout(self.__actions_layout(name))
        return group

    def __actions_layout(self, name: str) -> QtW.QVBoxLayout:
        layout = QtW.QVBoxLayout()
        layout.setObjectName(f"{name}_layout")
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtC.Qt.AlignCenter)
        layout.addWidget(
            self.__button(
                name="verify",
                text="VERIFICAR\nArquivos de Des.\nFaltantes",
                xy=(120, 60),
                lock=False,
            )
        )
        layout.addWidget(
            self.__button(
                name="mkfolders",
                text="GERAR\nPastas com Arq.\nde Desenhos",
                xy=(120, 60),
                lock=False,
            )
        )
        layout.addWidget(
            self.__button(name="help", text="Ajuda Rápida", xy=(120, 35))
        )
        return layout

    def __input_group(self, name: str, text: str) -> QtW.QGroupBox:
        group = QtW.QGroupBox()
        group.setObjectName(f"{name}_group")
        group.setMinimumSize(140, 70)
        group.setMaximumSize(200, 70)
        group.setContentsMargins(0, 0, 0, 0)
        group.setLayout(self.__input_layout(name, text))
        return group

    def __input_layout(self, name: str, text: str) -> QtW.QVBoxLayout:
        layout = QtW.QVBoxLayout()
        layout.setObjectName(f"{name}_layout")
        layout.addWidget(self.__label(name, text, (180, 16)))
        line_edit = self.__line_edit(name, (180, 25), False)
        layout.addWidget(line_edit)
        self.input_dict[name] = line_edit
        return layout

    def __menubar(self, parent: QtW.QMainWindow):
        menu_bar = QtW.QMenuBar(parent)
        config_menu = QtW.QMenu("Configurações", parent)
        config_menu.addAction(
            self.__action(
                name="config",
                parent=parent,
                action_text="Painel de Configurações",
                tooltip_text="Configurações do aplicativo.",
            )
        )
        config_menu.addAction(
            self.__action(
                name="restore",
                parent=parent,
                action_text="Restaurar",
                tooltip_text="Restaura configurações padrão.",
            )
        )
        help_menu = QtW.QMenu("Ajuda", parent)
        help_menu.addAction(
            self.__action(
                name="help",
                parent=parent,
                action_text="Ajuda",
                tooltip_text="Abre a caixa de ajuda.",
            )
        )
        menu_bar.addMenu(config_menu)
        menu_bar.addSeparator()
        menu_bar.addMenu(help_menu)
        return menu_bar

    def __button(
        self, name: str, text: str, xy: tuple, lock: bool = True
    ) -> QtW.QPushButton:
        button = QtW.QPushButton()
        button.setFixedSize(xy[0], xy[1])
        button.setText(text)
        button.setObjectName(f"{name}_button")
        button.setEnabled(lock)
        return button

    def __label(self, name: str, text: str, xy: tuple) -> QtW.QLabel:
        label = QtW.QLabel()
        label.setFixedSize(xy[0], xy[1])
        label.setText(text)
        label.setObjectName(f"{name}_label")
        return label

    def __line_edit(
        self, name: str, xy: tuple, lock: bool = True
    ) -> QtW.QLineEdit:
        line_edit = QtW.QLineEdit()
        line_edit.setFixedSize(xy[0], xy[1])
        line_edit.setObjectName(f"{name}_line")
        line_edit.setReadOnly(lock)
        return line_edit

    def __action(
        self,
        name: str,
        parent: QtC.QObject,
        action_text: str,
        tooltip_text: str,
    ) -> QtW.QAction:
        action = QtW.QAction(action_text, parent)
        action.setObjectName(f"{name}_action")
        action.setText(action_text)
        action.setToolTip(tooltip_text)
        return action

# -----------------------------------------------------------------------------
# 03 => JANELA DE CONFIGURAÇÕES

class ConfigDialog(QtW.QDialog):
    def __init__(self, parent: QtW.QMainWindow):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setMinimumSize(100, 100)
        self.setLayout(self.__main_layout())
        self.setFont(font())
        self.setModal(True)

        self.ext_regex = QtC.QRegExp(r"^[a-zA-Z]+(\+[a-zA-Z]+)*$")
        self.findChild(QtW.QPushButton, "pb_cancel").clicked.connect(
            self.reject
        )

    def __main_layout(self) -> QtW.QVBoxLayout:
        layout = QtW.QVBoxLayout()
        layout.addWidget(
            self.__config_group(
                title="Extensões: Verificar",
                name="ext_verify",
                placeholder="Digite extensões, ex: pdf+dwg+igs",
                tooltip="Separar com '+'",
            )
        )
        layout.addWidget(
            self.__config_group(
                title="Extensões: Copiar",
                name="ext_copy",
                placeholder="Digite extensões, ex: pdf+dwg+igs",
                tooltip="Separar com '+'",
            )
        )
        layout.addWidget(self.__button("pb_edit", "Alterar"))
        layout.addWidget(self.__button("pb_save", "Salvar"))
        layout.addWidget(self.__button("pb_cancel", "Cancelar"))
        return layout

    def __config_group(
        self, title: str, name: str, placeholder: str, tooltip: str
    ) -> QtW.QGroupBox:
        group = QtW.QGroupBox(title)
        group.setObjectName(f"{name}_group")
        group.setLayout(self.__config_layout(name, placeholder, tooltip))
        return group

    def __config_layout(
        self, name: str, placeholder: str, tooltip: str
    ) -> QtW.QVBoxLayout:
        layout = QtW.QVBoxLayout()
        layout.setObjectName(f"{name}_layout")
        layout.addWidget(self.__line_edit(name, placeholder, tooltip))
        return layout

    def __line_edit(
        self, name: str, placeholder: str, tooltip: str
    ) -> QtW.QLineEdit:
        line_edit = QtW.QLineEdit()
        line_edit.setObjectName(f"{name}_le")
        line_edit.setMinimumSize(250, 25)
        line_edit.setReadOnly(True)
        line_edit.setEnabled(False)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setToolTip(tooltip)
        line_edit.setToolTipDuration(5000)
        regex = QtC.QRegExp(r"^[a-zA-Z]+(\+[a-zA-Z]+)*$")
        validator = QtG.QRegExpValidator(regex, line_edit)
        line_edit.setValidator(validator)
        return line_edit

    def __button(self, name: str, text: str) -> QtW.QPushButton:
        button = QtW.QPushButton()
        button.setObjectName(name)
        button.setMinimumSize(90, 25)
        button.setText(text)
        return button

# -----------------------------------------------------------------------------
# 04 => JANELA DE AJUDA RÁPIDA

class QuickHelpBox(QtW.QMessageBox):
    def __init__(self, parent: QtW.QMainWindow):
        super().__init__(parent)
        self.setWindowTitle("Orientações Rápidas")
        self.setMaximumWidth(300)
        self.setText(self.help_text())
        self.setInformativeText(self.info_text())
        self.setStandardButtons(QtW.QMessageBox.Ok)
        self.setIcon(QtW.QMessageBox.Information)

    def help_text(self):
        return str(
            "COMO UTILIZAR:\n\n"
            "1. Selecione o arquivo que contém a tabela com a lista de "
            "códigos.\n"
            "2. Selecione a pasta onde estão salvos os arquivos de desenho.\n"
            "3. Se deseja utilizar a função GERAR, selecione também o local "
            "onde serão criadas as pastas.\n"
            "4. Confira e preencha de acordo com a sua necessidade os campos "
            "de parâmetros, informando a coluna com os códigos, a coluna com "
            "as palavras-chave, e as palavras-chave que deseja utilizar.\n"
            "5. Pressione o botão de ação desejado e acompanhe o resultado "
            "pelo próprio terminal de mensagens do aplicativo.\n"
            "\nPara maiores informações, selecione a opção Ajuda na barra "
            "de ferramentas superior."
        )

    def info_text(self):
        return str("Aplicativo TOX-Utilities.\nVersão: 1.0\nAutor: FSantos")

# -----------------------------------------------------------------------------
# 05 => JANELA DE MENSAGEM

class MsgBox(QtW.QMessageBox):
    def __init__(self, parent: QtW.QMainWindow, title, msg, btns: tuple = ("Sim", "Não")):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(msg)
        self.setIcon(QtW.QMessageBox.Question)

        # Cria botões
        button1 = QtW.QPushButton(btns[0])
        button1.setObjectName('button1')
        button2 = QtW.QPushButton(btns[1])
        button2.setObjectName('button2')
        button3 = QtW.QPushButton("Cancelar")
        button3.setObjectName('cancel')

        # Adicionar os botões à QMessageBox
        self.addButton(button1, QtW.QMessageBox.AcceptRole)
        self.addButton(button2, QtW.QMessageBox.RejectRole)
        self.addButton(button3, QtW.QMessageBox.ResetRole)

        # Exibe a caixa de dialogo
        self.exec_()

# -----------------------------------------------------------------------------
# 06 => JANELA DE DIALOGO

class DialogBox(QtW.QDialog):
    def __init__(self, title: str, msg: str, btns: tuple = ("OK", "Não"), lst: list = None):
        self.setWindowTitle(title)
        self.setMinimumSize(300, 150)
        # Criar layout vertical
        layout = QtW.QVBoxLayout()
        # Criar label de instrução
        qd_label = QtW.QLabel(msg)
        layout.addWidget(qd_label)
        # Criar widget lista ou linha editável de acordo com parametro
        if lst:
            opt_input = QtW.QListWidget()
            opt_input.addItems(lst)
            opt_input.setSelectionMode(QtW.QListWidget.SingleSelection)
            opt_input.setCurrentRow(0)
        else:
            opt_input = QtW.QLineEdit()
        layout.addWidget(opt_input)
        # Cria botões
        button1 = QtW.QPushButton(btns[0])
        button2 = QtW.QPushButton(btns[1])
        button3 = QtW.QPushButton("Cancelar")
        button1.clicked.connect(lambda: self.done(0))
        button2.clicked.connect(lambda: self.done(1))
        button3.clicked.connect(lambda: self.done(2))
        layout.addWidget(button1)
        if isinstance(opt_input, QtW.QLineEdit):
            layout.addWidget(button2)
        layout.addWidget(button3)
        # Aplicar o layout ao QDialog
        self.setLayout(layout)

        # Executar o diálogo e processar o resultado
        self.exec_()
    
        if self.result() in (0, 1):
            if isinstance(opt_input, QtW.QListWidget):
                self.text = opt_input.currentItem().text()
            else:
                self.text = opt_input.text()
        else:
            self.text = str('')

# -----------------------------------------------------------------------------
# 07 => GERENCIADOR DE MENSAGENS

class TextStream(QtC.QObject):
    text_written = QtC.pyqtSignal(str)
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.text_written.connect(self.write_to_widget)

    def write(self, text):
        self.text_written.emit(text)

    def flush(self):
        pass

    @QtC.pyqtSlot(str)
    def write_to_widget(self, text):
        self.widget.insertPlainText(text)
        self.widget.ensureCursorVisible()

# -----------------------------------------------------------------------------
# 08 => FUNÇÕES AUXILIARES PARA TESTE INDEPENDENTE

def font() -> QtG.QFont:
    custom_font = QtG.QFont()
    custom_font.setFamily("MS Shell Dlg 2")
    custom_font.setPointSize(10)
    custom_font.setBold(False)
    custom_font.setWeight(50)
    custom_font.setKerning(True)
    return custom_font

def config_widget(parent):
    if isinstance(parent, QtW.QMainWindow):
        config_window = ConfigDialog(parent)
        config_window.show()

def help_box(parent):
    if isinstance(parent, QtW.QMainWindow):
        help_window = QuickHelpBox(parent)
        help_window.show()

# -----------------------------------------------------------------------------
# 09 => EXECUÇÃO

if __name__ == "__main__":
    app = QtW.QApplication(sys.argv)
    main_view = MainUserInterface("TOX-Utilities")
    main_view.show()
    main_view.findChild(QtW.QAction, "config_action").triggered.connect(
        lambda: config_widget(main_view)
    )
    main_view.findChild(QtW.QPushButton, "help_button").clicked.connect(
        lambda: help_box(main_view)
    )
    sys.exit(app.exec_())
