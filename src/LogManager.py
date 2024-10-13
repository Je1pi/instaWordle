import os
from datetime import datetime

class LogManager:
    def __init__(self, log_dir: str = "logs"):
        """
        Inicializa o gerenciador de logs.

        :param log_dir: O diretório onde os arquivos de log serão armazenados.
        """
        current_directory = os.path.dirname(os.path.realpath(__file__))
        self.log_dir = os.path.join(current_directory, log_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.current_log_file = self._get_log_file()
        self.last_messages = []

        self._log_initialization()

    def _get_log_file(self) -> str:
        """
        Retorna o nome do arquivo de log baseado na data atual.

        :return: O caminho do arquivo de log para a data atual.
        """
        return os.path.join(self.log_dir, f"{self.current_date}.log")

    def _update_log_file_if_needed(self) -> None:
        """
        Atualiza o arquivo de log se o dia tiver mudado.
        Se o dia mudou, o arquivo de log é atualizado para o novo dia e as mensagens
        anteriores são limpas.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.current_date:
            self.current_date = today
            self.current_log_file = self._get_log_file()
            self.last_messages.clear()

    def _log_initialization(self) -> None:
        """
        Registra a nova inicialização no arquivo de log, se já existir.
        Se o arquivo de log já existe, uma nova seção de inicialização é adicionada.
        """
        if os.path.exists(self.current_log_file):
            with open(self.current_log_file, "a") as log_file:
                log_file.write("\n\n[New Initialization]\n\n")

    def addToLog(self, log_message: str) -> None:
        """
        Adiciona uma nova mensagem ao arquivo de log com a hora atual.
        Se a mensagem for igual às duas últimas mensagens, ela será ignorada.

        :param log_message: A mensagem a ser registrada no log.
        """
        self._update_log_file_if_needed()
        if log_message in self.last_messages:
            return

        self.last_messages.append(log_message)
        if len(self.last_messages) > 2:
            self.last_messages.pop(0)

        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {log_message}\n"

        with open(self.current_log_file, "a") as log_file:
            log_file.write(log_entry)