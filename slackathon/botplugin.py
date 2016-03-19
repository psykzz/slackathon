from yapsy.IPlugin import IPlugin


class BotPlugin(IPlugin):
    def __init__(self):
        self.bot = None
        super().__init__()

    def attach_bot(self, bot):
        self.bot = bot
