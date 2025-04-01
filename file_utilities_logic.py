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
import inspect
from xml.etree import ElementTree
import pandas as pd
import unidecode as ud
import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import PyQt5.QtGui as QtG
from file_utilities_model import ConfigMain

class Verifier():
    def selection_dict_str(self, current_dict: dict):
        logger = logging.getLogger(__name__)
        new_dict = {}
        fname = inspect.currentframe().f_code.co_name
        # Preenche nomes
        for key, value in current_dict.items():
            if isinstance(key, QtW.QPushButton):
                key = key.objectName()
            if isinstance(value, QtW.QLineEdit):
                value = value.text()
            new_dict[key] = value
            logger.debug(f'Method: {fname} Entry => {key} : {value}')
        return new_dict

    def verify_exec(self, user_selections: dict, user_input: dict):
        # Ler arquivo de tabela
        table_df = self.find_and_read_table(user_selections)

        # Gera lista com todos os códigos relacionados as palavras-chave
        code_list = self.code_list()

        # Nome do arquivo de relatorio
        log_name = f"log_arquivos_faltantes_{time_reg[3]}_{time_reg[2]}.txt"
        # Caminho do relatorio de arquivos faltantes
        log_path = os.path.join(os.path.dirname(tbl_path), log_name)

        # Cria cabeçalho do relatorio
        start_msg = (
            f"Relatório gerado em {time_reg[1]} as {time_reg[0]}hrs."
            f"\n\nDados Informados pelo usuário:\n"
            f"\nArquivo-Tabela selecionado: {tbl_path}"
            f"\nPasta com arquivos originais: {src_fld_path}"
            f"\nColuna com códigos: {col_cod}"
            f"\nColuna com palavra-chave: {kw_col}"
            f"\nPalavras-Chave: {kw_list}"
            f"\n"
            f"\nNão foi possível encontrar alguns arquivos. "
            f"Segue abaixo lista dos arquivos faltantes."
            f"\n\n"
        )

        # Sinal de falta de extensão, para mostrar mensagem correta
        flag_abs = False

        # Itera sobre cada código verificando a existência dos arquivos
        for code in code_list:
            code = str(code)  # Redundancia
            # Lista todos os arquivos com o código informado presente no nome
            found_files = [
                os.path.split(file)[1].lower()
                for file in fls_list
                if re.search(code, os.path.split(file)[1].lower(), re.I)
            ]
            # Lista as extensões dos arquivos listados
            found_ext = [os.path.splitext(file)[1] for file in found_files]
            # Lista as extensões que não foram encontradas
            abs_ext = [ext for ext in file_types if ext not in found_ext]
            # Se houver falta de alguma extensão, salva mensagem informativa
            if abs_ext:
                flag_abs = True  # Sinaliza a falta
                # Verifica se o relatório já existe
                if os.path.exists(log_path):
                    with open(log_path, mode="a") as log_file:
                        for ext in abs_ext:
                            msg = f"Arquivo '{ext}' não encontrado para o código '{code}'"
                            self.logger.info(msg)
                            log_file.write(msg + "\n")
                else:
                    with open(log_path, mode="a") as log_file:
                        log_file.write(start_msg)
                        for ext in abs_ext:
                            msg = f"Arquivo '{ext}' não encontrado para o código '{code}'"
                            self.logger.info(msg)
                            log_file.write(msg + "\n")
        if flag_abs:
            self.logger.info(
                f"Salvo relatório com a relação de arquivos faltantes."
                f"\nLocal do arquivo salvo: {log_path}"
            )
        else:
            self.logger.info("Não foi encontrado nenhum arquivo faltante.")

    def code_list(self, table_df: pd.DataFrame, code_col: str, kw_col: str, kw_list: list) -> list:
        # Gera lista com todos os códigos relacionados as palavras-chave
        code_list = []
        for kw in kw_list:
            partial_df = (
                table_df.loc[
                    table_df[kw_col].str.contains(kw, case=False, na=False)
                ]
                .drop(labels=kw_col, axis=1)
                .reset_index(drop=True)
            )
            partial_list = list(set(partial_df[code_col].dropna().tolist()))
            for item in partial_list:
                code_list.append(item)
        return code_list

    def find_and_read_table(self, user_selections: dict) -> pd.DataFrame:
        logger = logging.getLogger(__name__)
        fname = inspect.currentframe().f_code.co_name
        try:
            filepath = [value for key, value in user_selections if 'table' in key]
            if len(filepath) > 1:
                logger.debug(f'Função: {fname}. Erro: mais de um item na lista de valores.')
                raise Exception('Erro na identificação do caminho da tabela.')
            return self.read_table_file(filepath)

        except Exception as e_obj:
            logger.error(traceback.format_exc())
            logger.error(f"Error: {str(e_obj)}")

    # Abre o arquivo com tabela e retorna um dataframe "virgem"
    def read_table_file(self, filepath):
        """Read table file based on its extension."""
        logger = logging.getLogger(__name__)
        file_ext = os.path.splitext(filepath)[1].lower()
        if file_ext in ('.xlsx', '.xlsm'):
            ws_list = pd.ExcelFile(filepath).sheet_names
            treated_ws_list = [ud.unidecode(ws).lower() for ws in ws_list]
            if len(treated_ws_list) > 1:
                user_ans = self.dialog_box(
                    title='Multiplas planilhas',
                    msg='Foram encontradas múltiplas planilhas no arquivo '
                        'especificado.\nSelecione a planilha desejada abaixo:',
                    lst=ws_list
                )
                if user_ans[0] is True:
                    sht_n = user_ans[1]
                else:
                    self.logger.error(
                        'Processo abortado: Falta definição de planilha.')
                    return None, file_ext
            else:
                sht_n = ws_list[0]
        else:
            sht_n = 0
        # Funções de leitura
        readers = {
            ".csv": lambda fp: pd.read_csv(
                filepath_or_buffer=fp,
                sep=";",
                header=0,
                dtype=str,
                encoding="ISO-8859-1",
                on_bad_lines="warn"),
            ".xlsx": lambda fp: pd.read_excel(
                io=fp, sheet_name=sht_n, dtype=str),
            ".xlsm": lambda fp: pd.read_excel(
                io=fp, sheet_name=sht_n, dtype=str),
            ".xml": self._read_xml
        }
        if file_ext not in readers:
            self.logger.error(f"Formato de arquivo não suportado: {file_ext}")
            return None, file_ext
        try:
            table_df = readers[file_ext](filepath)
            df_cols = len(table_df.columns)
            new_index = list(itertools.islice(self._cols_index(), df_cols))
            table_df.columns = new_index
            return table_df, file_ext
        except Exception as except_obj:
            self.logger.error(f"Erro lendo arquivo {filepath}: {str(except_obj)}")
            traceback.print_exc()
            return None, file_ext

    # Função auxiliar para leitura específica de arquivos XML
    def _read_xml(self, filepath):
        """Helper function to read XML files."""
        try:
            # Parsear o XML
            tree = ElementTree.parse(filepath)
            root = tree.getroot()
            # Namespace
            ns = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}
            # Encontrar todas as linhas da tabela
            rows = root.findall(".//ss:Row", ns)
            # Extrair cabeçalhos (segunda linha, índice 1)
            headers = [
                cell.find("ss:Data", ns).text
                for cell in rows[1].findall("ss:Cell", ns)
            ]
            # Extrair dados (a partir da terceira linha, índice 2)
            data = []
            # Ignora a primeira linha (título) e a segunda (cabeçalhos)
            for row in rows[2:]:
                cells = row.findall("ss:Cell", ns)
                row_data = []
                for cell in cells:
                    data_elem = cell.find("ss:Data", ns)
                    row_data.append(
                        data_elem.text if data_elem is not None else ""
                    )
                data.append(row_data)
            # Criar DataFrame
            table_df = pd.DataFrame(data, columns=headers)
            return table_df
        except Exception as except_obj:
            self.logger.error(f"Erro analisando arquivo XML. Erro: {str(except_obj)}")
            traceback.print_exc()
            return None


    # Processa um 'list' ou 'string' em uma lista única de palavras-chave
    def process_keywords(self, kw_input, kw_col=None, sep="+"):
        """Processa uma sequência ou lista de palavras-chave em uma lista 
        exclusiva de palavras-chave."""
        if isinstance(kw_input, str):
            keywords = kw_input.split(sep)
        elif isinstance(kw_input, pd.DataFrame):
            keywords = list(set(kw_input[kw_col].dropna().tolist()))
        else:
            self.logger.warning('Fonte de palavras-chave não reconhecida.')
            return []
        flat_keywords = []
        for kw in keywords:
            flat_keywords.extend(kw.split(sep) if sep in kw else [kw])
        return list(set(flat_keywords))

    # Retorna um registro com horário e data do momento de execução
    def time_register(self):
        time_var = time.localtime()
        cur_time = time.strftime(r"%H:%M:%S", time_var)
        cur_date = time.strftime(r"%d/%m/%Y", time_var)
        txt_time = time.strftime(r"%H-%M-%S", time_var)
        txt_date = time.strftime(r"%d-%m-%Y", time_var)
        time_reg = [cur_time, cur_date, txt_time, txt_date]
        return time_reg

    # Copiar lote de arquivos para um local informado
    def copy_file_batch(self, files_list, dst_fld):
        error_flag = False
        if not files_list:
            self.logger.error(f'Lista a copiar vazia. Pasta destino: {dst_fld}')
            return None
        for filepath in files_list:
            filename = os.path.basename(filepath)
            future_filename = os.path.join(dst_fld, filename)
            # Confere se o desenho a ser copiado ja existe
            if os.path.exists(future_filename):
                self.logger.warning(
                    f"Arquivo '{filename}' já existe na pasta '{dst_fld}'"
                    f" e não será copiado."
                )
                continue
            else:
                shutil.copy(src=filepath, dst=dst_fld)
                if not os.path.exists(future_filename):
                    error_flag = True
        dest_fld_n = os.path.basename(dst_fld)
        if error_flag:
            self.logger.error(
                "Ocorreu um problema ao copiar os arquivos para a pasta "
                f"{dest_fld_n}. Favor verificar."
            )
        else:
            self.logger.info(
                f"Arquivos copiados com sucesso para pasta '{dest_fld_n}'"
            )

    # Filtra 'dataframe' por uma palavra-chave em um coluna e retorna em lista
    def code_list_from_df(self, df, kw, kw_col, cod_col):
        pre_list = df.loc[df[kw_col].str.split('+').apply(lambda x: kw in x)]
        code_list = list(pre_list[cod_col])
        return code_list



    # Retorna lista com todos os arquivos dentro de um diretório
    # Incluindo os subdiretórios subsequentes
    def list_folder_files(self, folderpath):
        if os.path.isdir(folderpath):
            files_list = []
            for path, subdirs, files in os.walk(folderpath):
                for file in files:
                    files_list += [os.path.normpath(os.path.join(path, file))]
            return files_list
        else:
            self.logger.error('Informação não é um caminho de pasta.')
            return None
    
    # Gerador de rótulos estilo "Excel" para colunas do dataframe
    def _cols_index(self):
        n = 1
        while True:
            yield from (
                "".join(group)
                for group in itertools.product(
                    string.ascii_uppercase, repeat=n
                )
            )
            n += 1

    # Criador de pastas/diretórios
    def make_dir(self, dir_path, dir_name):
        full_dir_name = os.path.join(dir_path, dir_name)
        if os.path.exists(full_dir_name):
            return full_dir_name, True
        else:
            os.mkdir(full_dir_name)
            if os.path.exists(full_dir_name):
                self.logger.info(f"Pasta '{dir_name}' criada com sucesso.")
            return full_dir_name, False

    # Deleta pastas/diretórios
    def del_dir(self, dir_path, dir_name):
        try:
            full_dir_name = os.path.join(dir_path, dir_name)
            if os.path.exists(full_dir_name):
                shutil.rmtree(path=full_dir_name)
                if not os.path.exists(full_dir_name):
                    self.logger.info(f"Pasta '{dir_name}' excluída com sucesso.")
                    return True
                else:
                    self.logger.warning(
                        f"Pasta '{dir_name}' não excluída. Favor verificar."
                    )
                    return False
            else:
                self.logger.warning(
                    f"Pasta '{dir_name}' não encontrada, favor verificar."
                )
                return False
        except Exception as except_obj:
            self.logger.error(f"Erro excluindo pasta '{dir_name}'."
                  f" Erro: {str(except_obj)}")
            traceback.print_exc()
            return None

    def build_file_index(self, files_list):
        """Cria um índice de arquivos por nome base (sem extensão)."""
        file_index = {}
        for file in files_list:
            filename = os.path.split(file)[1].lower()
            base_name, ext = os.path.splitext(filename)
            if ext not in file_index:
                file_index[ext] = {}
            file_index[ext][base_name] = file
        return file_index

    def filter_files(self, code_list, files_list):
        """Filtra arquivos usando um índice pré-construído."""
        extensions = str(self.config.copy_ext).split("+")
        file_index = self.build_file_index(files_list)
        filepath_list = []
        for code in code_list:
            code = code.lower()
            for ext in extensions:
                if ext.startswith('.'):
                    ext_key = ext
                else:
                    ext_key = f".{ext}"
                if ext_key in file_index and code in file_index[ext_key]:
                    filepath_list.append(file_index[ext_key][code])
        if filepath_list:
            self.logger.info("Arquivos filtrados por código.")
            return list(set(filepath_list))
        else:
            self.logger.error(
                'Lista de arquivos filtrados: Vazia. Favor verificar.'
            )
            return None
