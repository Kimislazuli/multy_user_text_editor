class Logger:
    def __init__(self, log_file_name: str):
        self.file = open(log_file_name, 'a')

    def log(self, text: str):
        self.file.write(f"{text}\n")