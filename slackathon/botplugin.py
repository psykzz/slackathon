from yapsy.IPlugin import IPlugin


class BotPlugin(IPlugin):
    def __init__(self):
        self.bot = None
        self.channels = None
        self.users = None
        self.client = None
        super().__init__()

    def attach_bot(self, bot):
        self.bot = bot
        self.channels = bot.server.channels
        self.users = bot.server.users
        self.client = bot.client

    def api_call(self, *args, **kwargs):
        return self.client.api_call(*args, **kwargs)

    def send(self, channel, message, **kwargs):
        if kwargs:
            self.client.api_call("chat.postMessage", channel=channel, message=message, **kwargs)
        else:
            self.client.rtm_send_message(channel, message)