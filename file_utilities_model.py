# ----------------------------------------------------------------------------

# CONCEITOS GERAIS:
# Manter régua de limite em 80 caracteres por linha.
# Nomes em Inglês, abreviados sempre que possível, para manter a régua.
# Documentaçao (Comentários, anotações e 'docstrings') em Português-Br.

# ----------------------------------------------------------------------------
# 01 => IMPORTACOES DE MODULOS

import logging
import sys
import json
import os

# ----------------------------------------------------------------------------
# 02 => CLASSE DE CONFIGURAÇÃO

class ConfigMain():
    '''Objeto tipo 'model' (arquiteturas MVC) que garante a existência de 
    arquivo de configuração tipo JSON e o manipula conforme solicitado '''
    def __init__(self):
        self.config_folder = self.check_config_folder()
        self.config_file = self.check_config_file(self.config_folder)
        # Verificar valores padrão
        self.check_default_values(self.config_file)

    def check_config_folder(self) -> str:
        # Declara nomes conforme o sistema operacional em execução
        logger = logging.getLogger(__name__)
        if sys.platform == 'win32':
            base_folder = 'APPDATA'
            main_name = 'TOX-Utilities'
        elif sys.platform == 'linux':
            base_folder = 'HOME'
            main_name = '.config/TOX-Utilities'
        else:
            config_folder = os.path.dirname(os.path.abspath(__file__))
            logger.error(
                'Não foi possível identificar sistema operacional.')
            return config_folder
        # Define o caminho completo da pasta de configurações
        config_folder = os.path.abspath(
                os.path.join(os.getenv(base_folder), main_name)
        )
        if os.path.isdir(config_folder):
            logger.info("Pasta de configuracoes existente. Prosseguindo.")
            return config_folder
        else:
            logger.info(
                "Pasta de configuracoes nao encontrada. Criando uma nova."
            )
            os.mkdir(config_folder)
            return config_folder

    def check_config_file(self, config_folder) -> str:
        logger = logging.getLogger(__name__)
        config_file = os.path.join(
            config_folder,
            'TOX-Utilities_config.json'
        )
        if os.path.exists(config_file):
            logger.info("Arquivo de configuracoes existente. Prosseguindo.")
            return config_file
        with open(config_file, "w") as file:
            json.dump(self.default_config(), file)
        logger.info("Arquivo de configuracoes inexistente. Criando novo.")
        return config_file

    def check_default_values(self, config_file) -> None:
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                json_file = json.load(file)
            default_config = self.default_config()
            updated = False
            # Confere se os registros da configuração padrão existem no
            # arquivo encontrado e cria o registro se ele não existir.
            for key, value in default_config.items():
                if key not in json_file:
                    json_file[key] = value
                    updated = True
            # Confere se o registro está vazio e se existe configuração
            # padrão. Se verdadeiro, atualiza o registro com o valor da
            # configuração padrão.
            for key, value in json_file.items():
                if value == '' and key in default_config:
                    json_file[key] = value
                    updated = True
            # Grava informações
            if updated:
                with open(config_file, 'w') as file:
                    json.dump(json_file, file)

    def default_config(self) -> dict:
        root_folder = os.path.dirname(os.path.abspath(__file__))
        default_config = {
            "verify_ext": "pdf+dwg+igs",
            "copy_ext": "pdf+dwg+igs+step+pvz",
            "cod_col": "B",
            "kw_col": "I",
            "kw": "BR-PROD-MA+BR-WELD-MA",
            "last_fld": root_folder
        }
        return default_config

    def get_value(self, key) -> any:
        '''Carregar arquivo JSON e retornar o valor solicitado'''
        with open(self.config_file, 'r') as file:
            json_file = json.load(file)
            if key not in json_file:
                raise ValueError('Configuração não encontrada.')
            if json_file[key]:
                return json_file[key]
            else:
                raise ValueError('Configuração com registro vazio.')

    def set_value(self, key, value, new=False) -> tuple:
        '''Carregar arquivo JSON e gravar valor solicitado no arquivo (retorna 
        o resultado da gravação)'''
        with open(self.config_file, 'r') as file:
            json_file = json.load(file)
        if key in json_file or new is True:
            json_file[key] = value
            with open(self.config_file, 'w') as file:
                json.dump(json_file, file)
            return True, f"Configuração '{key}' gravada."
        if key not in json_file:
            return False, f"Configuração '{key}' inexistente."

if __name__ == "__main__":
    config_main = ConfigMain()