from yapsy.IPlugin import IPlugin


class BotPlugin(IPlugin):
    def __init__(self):
        self.bot = None
        self.channels = None
        self.users = None
        self.server = None
        super().__init__()

    def attach_bot(self, bot):
        self.bot = bot
        self.channels = bot.server.channels
        self.users = bot.server.users
        self.server = bot.server
