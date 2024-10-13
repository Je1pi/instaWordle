import os
from datetime import datetime

class LogManager:
    def __init__(self, log_dir="logs"):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        self.log_dir = os.path.join(current_directory, log_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.current_log_file = self._get_log_file()

        self._log_initialization()

    def _get_log_file(self):
        """Retorna o nome do arquivo de log baseado na data atual."""
        return os.path.join(self.log_dir, f"{self.current_date}.log")

    def _update_log_file_if_needed(self):
        """Atualiza o arquivo de log se o dia tiver mudado."""
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.current_date:
            self.current_date = today
            self.current_log_file = self._get_log_file()

    def _log_initialization(self):
        """Registra a nova inicialização no arquivo de log, se já existir."""
        if os.path.exists(self.current_log_file):
            with open(self.current_log_file, "a") as log_file:
                log_file.write("\n\n[New Initialization]\n\n")

    def addToLog(self, log_message):
        """Adiciona uma nova mensagem ao arquivo de log com a hora atual."""
        self._update_log_file_if_needed()

        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {log_message}\n"

        with open(self.current_log_file, "a") as log_file:
            log_file.write(log_entry)