import inspect

class Commands:
    def __init__(self):
        self.commands = {}

    def appendCommand(self, command, func, errorFunc=None):
        self.commands[command] = {"func": func, "errorFunc": errorFunc}

    def runCommand(self, msg, client, *args, **kwargs):
        command, msgArgs = self.separateCommand(msg)
        msgArgs = msgArgs.split() if msgArgs else []

        if command in self.commands:
            func = self.commands[command]["func"]
            sig = inspect.signature(func)
            num_params = len(sig.parameters) - len(args) - len(kwargs) - 1

            if len(msgArgs) < num_params or len(msgArgs) > num_params:
                return self.runErrorFunc(command, client, *args, **kwargs)

            return func(client, *msgArgs[:num_params], *args, **kwargs)
    
    def runErrorFunc(self, command, client, *args, **kwargs):
        errorFunc = self.commands[command].get("errorFunc")
        if errorFunc:
            try:
                return errorFunc(client, *args, **kwargs)
            except Exception as e:
                pass
        else:
            pass

    def isCommand(self, msg):
        command, _ = self.separateCommand(msg)
        return command in self.commands
    
    def separateCommand(self, msg):
        parts = msg.split()
        command = parts[0].lstrip('/')
        return command, ' '.join(parts[1:]) if len(parts) > 1 else None