class Commands:
    def __init__(self):
        self.commands = {}

    def appendCommand(self, command, func):
        self.commands[command] = func

    def execCommand(self, message, *args, **kwargs):
        parts = message.split()
        commandTemp = parts[0]
        commandArgs = parts[1:]

        if commandTemp.startswith("/"):
            commandTemp = commandTemp[1:]

        if commandTemp in self.commands:
            return self.commands[commandTemp](*args, *commandArgs, **kwargs)
        else:
            raise ValueError("Comando não encontrado.")
    
    def isCommand(self, arg):
        argTemp = arg
        if arg.startswith("/"):
            argTemp = arg[1:]
        return argTemp in self.commands