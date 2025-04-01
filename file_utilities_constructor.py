# ----------------------------------------------------------------------------

# CONCEITOS GERAIS:
# Manter régua de limite em 80 caracteres por linha.
# Nomes em Inglês, abreviados sempre que possível, para manter a régua.
# Documentaçao (Comentários, anotações e 'docstrings') em Português-Br.

# ----------------------------------------------------------------------------
# 01 => IMPORTACOES DE MODULOS

import sys
import traceback
import os
import re
import itertools
import string
import time
import shutil
import json
import logging
from xml.etree import ElementTree
from pathlib import Path
import pandas as pd
import unidecode as ud
import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import PyQt5.QtGui as QtG
import file_utilities_model as TUtM
import file_utilities_view as TUtV
import file_utilities_logic as TUtL

# ----------------------------------------------------------------------------
# 02 => CLASSE GERENCIADORA

class UtilitiesConstructor():
    def __init__(self):
        # Cria instancia da janela principal
        self.main_window = self.__open_main_window()
        self.main_window.show()
        # Redireciona a saída de Print e Logger para o widget Terminal
        self.text_stream = TUtV.TextStream(
            widget = self.main_window.findChild(QtW.QPlainTextEdit, "terminal")
        )
        sys.stdout = self.text_stream
        # Configura sistema de logging para manter registro das mensagens
        self.__setup_logging()
        self.logger = logging.getLogger(__name__)
        # Abre instancia de classe gestora de configurações
        self.database = TUtM.ConfigMain()
        # Configura as regras de liberação e conexões dos widgets
        self.__buttons_enabler(parent=self.main_window)
        self.__aux_window_connections(parent=self.main_window)
        self.__buttons_connections(
            parent=self.main_window,
            database=self.database,
            select_dict=self.__selectors_dict(self.main_window)
        )

    def __open_main_window(self) -> QtW.QMainWindow:
        window = TUtV.MainUserInterface("TOX-Utilities")
        window.setObjectName('main_window')
        return window

    def __open_config_window(self, parent: TUtV.MainUserInterface) -> QtW.QDialog:
        if isinstance(parent, QtW.QMainWindow):
            window = TUtV.ConfigDialog(parent)
            window.show()
            return window

    def __quick_help_window(self, parent: TUtV.MainUserInterface) -> QtW.QMessageBox:
        if isinstance(parent, QtW.QMainWindow):
            window = TUtV.QuickHelpBox(parent)
            window.show()
            return window

    def __buttons_connections(self, parent: TUtV.MainUserInterface, database: TUtM.ConfigMain, select_dict: dict):
        file_kw = ['table_button']
        folder_kw = ['source_button', 'target_button']
        push_button_list = parent.findChildren(QtW.QPushButton)
        for item in push_button_list:
            if item.objectName() in file_kw:
                item.clicked.connect(lambda: self.__search_file(parent, database, select_dict))
            if item.objectName() in folder_kw:
                item.clicked.connect(lambda: self.__search_folder(parent, database, select_dict))
            if 'verify' in item.objectName():
                item.clicked.connect(lambda: self.__verify(parent))
            if 'mkfolder' in item.objectName():
                item.clicked.connect(lambda: self.__make_folders())

    def __aux_window_connections(self, parent: TUtV.MainUserInterface):
        # Configura conexão para a ação da barra de menus "Configurações"
        self.config_window = parent.findChild(QtW.QAction, "config_action").triggered.connect(lambda: self.__open_config_window(parent))
        # Configura conexão para a ação da barra de menus "Ajuda"
        self.help_window = parent.findChild(QtW.QPushButton, "help_button").clicked.connect(lambda: self.__quick_help_window(parent))

    def __buttons_enabler(self, parent: TUtV.MainUserInterface):
        for item in parent.findChildren(QtW.QLineEdit):
            item.textChanged.connect(lambda: self.__enable_buttons(parent))

    def __enable_buttons(self, parent: TUtV.MainUserInterface):
        line_edit_list = parent.findChildren(QtW.QLineEdit)
        push_button_list = parent.findChildren(QtW.QPushButton)

        flag_verify = True
        for item in line_edit_list:
            if "target" not in item.objectName() and not item.text():
                flag_verify = False
        if flag_verify is True:
            for item in push_button_list:
                if "verify" in item.objectName():
                    item.setEnabled(True)
        else:
            for item in push_button_list:
                if "verify" in item.objectName():
                    item.setEnabled(False)
        flag_mkfolders = True
        for item in line_edit_list:
            if "keyword_list" not in item.objectName() and not item.text():
                flag_mkfolders = False
        if flag_mkfolders is True:
            for item in push_button_list:
                if "mkfolder" in item.objectName():
                    item.setEnabled(True)
        else:
            for item in push_button_list:
                if "mkfolder" in item.objectName():
                    item.setEnabled(False)

    def __search_file(self, parent: TUtV.MainUserInterface, database: TUtM.ConfigMain, button_line: dict):
        sender = parent.sender()
        logger = logging.getLogger(__name__)
        filepath = QtW.QFileDialog.getOpenFileName(
            parent=parent,
            caption="Selecione um arquivo",
            directory=database.get_value('last_fld'),
            filter=str("Tabela (*.csv *.xls*);;XML GDView(*.xml);;Tudo (*.*)"),
        )
        # Escreve o caminho selecionado no 'lineEdit'
        if filepath[0]:
            button_line[sender].setText(str(filepath[0]))
            logger.info(
                f"Caminho do arquivo de tabela selecionado: {filepath[0]}"
            )
            # Atualiza 'config'
            database.set_value(
                key='last_fld',
                value=os.path.dirname(filepath[0]),
                new=True
            )
        else:
            logger.info("Nenhum arquivo foi selecionado.")

    def __search_folder(self, parent: TUtV.MainUserInterface, database: TUtM.ConfigMain, button_line: dict):
        sender = parent.sender()
        logger = logging.getLogger(__name__)
        folderpath = QtW.QFileDialog.getExistingDirectory(
            parent=parent,
            caption="Selecione uma pasta",
            directory=database.get_value('last_fld'),
            options=QtW.QFileDialog.ShowDirsOnly,
        )
        # Escreve o caminho selecionado no 'lineEdit'
        if folderpath:
            folderpath = QtC.QDir.cleanPath(folderpath)
            button_line[sender].setText(folderpath)
            logger.info(f"Pasta selecionada: {folderpath}")
            # Atualiza 'config'
            database.set_value(
                key='last_fld',
                value=folderpath,
                new=True
            )
        else:
            logger.info("Nenhuma pasta foi selecionada.")

    def __manage_log_files(self, diretorio, limite: int = 10):
        try:
            # Verifica se o diretório existe
            if not os.path.isdir(diretorio):
                raise ValueError(f"O diretório '{diretorio}' não existe.")
            # Lista todos os arquivos .log no diretório
            arquivos_log = [file for file in Path(diretorio).glob("*.log") if file.is_file()]
            # Se o número de arquivos for menor ou igual ao limite, não faz nada
            if len(arquivos_log) <= limite:
                return
            # Ordena os arquivos pela data de criação (do mais velho para o mais novo)
            arquivos_ordenados = sorted(arquivos_log, key=lambda x: x.stat().st_ctime)          
            # Calcula quantos arquivos precisam ser excluídos
            excedentes = len(arquivos_log) - limite
            arquivos_a_excluir = arquivos_ordenados[:excedentes]
            # Exclui os arquivos excedentes mais velhos
            for arquivo in arquivos_a_excluir:
                try:
                    arquivo.unlink()  # Remove o arquivo
                except Exception as e:
                    print(f"Erro ao excluir {arquivo}: {e}")
        except Exception as e:
            print(f"Erro ao gerenciar arquivos .log: {e}")

    def __setup_logging(self):
        # Determina a pasta base dependendo do sistema operacional
        if sys.platform == 'win32':
            base_folder = 'APPDATA'
            main_name = 'TOX-Utilities'
        elif sys.platform == 'linux':
            base_folder = 'HOME'
            main_name = '.config/TOX-Utilities'
        else:
            config_folder = os.path.dirname(os.path.abspath(__file__))
        config_folder = os.path.abspath(os.path.join(os.getenv(base_folder), main_name))
        if not os.path.isdir(config_folder):
            os.mkdir(config_folder)

        # Define o nome do arquivo de log com a data atual
        current_time = time.strftime(r"%Y-%m-%d", time.localtime())
        filename = f"Terminal_{current_time}.log"
        self.__manage_log_files(config_folder)
        filepath = os.path.join(config_folder, filename)
        # Configura o logger raiz com nível DEBUG (para capturar tudo)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Formato das mensagens de log
        log_format = logging.Formatter(
            fmt=r"%(asctime)s [%(levelname)s] %(message)s",
            datefmt=r'%d/%m/%Y-%H:%M:%S'
        )
        # Configura o FileHandler (salva tudo, nível DEBUG ou superior)
        file_handler = logging.FileHandler(filepath)
        file_handler.setLevel(logging.DEBUG)  # Garante que o arquivo capture DEBUG
        file_handler.setFormatter(log_format)

        # Configura o StreamHandler (mostra apenas INFO ou superior no terminal)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)  # Apenas INFO ou superior no terminal
        stream_handler.setFormatter(log_format)

        # Remove handlers antigos (se houver) e adiciona os novos
        logger.handlers.clear()
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)                           

    def deprecated_log(self, filepath):
        logging.basicConfig(
            level=logging.INFO,
            format=r"%(asctime)s [%(levelname)s] %(message)s",
            datefmt=r'%d/%m/%Y-%H:%M:%S',
            handlers=[
                logging.FileHandler(filepath),  # Arquivo de log
                logging.StreamHandler(sys.stdout)  # Mantém saída no terminal
            ]
        )

    def __selectors_dict(self, parent: TUtV.MainUserInterface) -> dict:
        buttons = parent.findChildren(QtW.QPushButton)
        line_edits = parent.findChildren(QtW.QLineEdit)
        pairs = {}
        # Para cada botão, encontrar o QLineEdit com o mesmo pai imediato
        for button in buttons:
            button_parent = button.parent()
            for line_edit in line_edits:
                if line_edit.parent() == button_parent:
                    pairs[button] = line_edit
                    break  # Assume que há apenas um QLineEdit por botão no mesmo pai
        return pairs

    def __verify(self, parent: TUtV.MainUserInterface):
        logger = logging.getLogger(__name__)
        logger.info('Chama o Verificador')
        try:
            # Dicionário de seleções do usuário
            selectors_dict = self.__selectors_dict(parent)  # Dict com objetos
            # Confere presença de dados (redundante)
            for key, value in selectors_dict.items():
                if not value.text():
                    logger.error(f'Processo abortado: Sem dados em {key.objectName()}')
                    return None

            # Questiona se o usuário conferiu o preenchimento
            conf_qstn = TUtV.MsgBox(
                parent=parent,
                title="CONFIRMACAO",
                msg=str(
                    "Conferiu o preenchimento das configurações de colunas?\n"
                    "Conferiu o preenchimento das palavras-chave?"
                )
            )
            if conf_qstn.clickedButton().objectName() == 'button2':
                return None
            del conf_qstn

            # Confirma presença dos dados inseridos pelo usuário
            for key, value in parent.input_dict.items():
                if not value.text():
                    logger.error(f'Processo abortado: Sem dados em {key}')
                    return None

            # Chama executor da verificação
            verificador = TUtL.Verifier(selectors_dict, parent.input_dict, TUtV.DialogBox)
            # verificador.verify_exec(selectors_dict, parent.input_dict, TUtV.DialogBox)

            logger.info('Verificação Concluída.')

        except Exception as e_obj:
            logger.error(traceback.format_exc())
            logger.error(f"Error: {str(e_obj)}")

    def __make_folders(self):
        try:
            print('Conectar classe de criação de pastas')
        except Exception as except_obj:
            self.logger.error(traceback.format_exc())
            self.logger.error(f"Error: {str(except_obj)}")
            raise

if __name__ == "__main__":
    app = QtW.QApplication(sys.argv)
    constructor = UtilitiesConstructor()
    sys.exit(app.exec_())
