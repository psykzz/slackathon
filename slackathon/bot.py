import logging
import os
import sys
import slackclient
import inspect

from yapsy.PluginManager import PluginManager
from yapsy.PluginFileLocator import PluginFileLocator, PluginFileAnalyzerWithInfoFile

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self, config):
        self.listen_commands = {}
        self.respond_commands = {}
        self.event_filters = []

        self.config = config
        self.client = slackclient.SlackClient(config.TOKEN)
        self.server = self.client.server

        # Setup plugins
        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(config.PLUGIN_PATHS)
        self.plugin_manager.collectPlugins()
        self.init_plugins()

    def init_plugins(self):
        for plugin_info in self.plugin_manager.getAllPlugins():
            logger.info("Loading plugin {}".format(plugin_info.name))
            self.plugin_manager.activatePluginByName(plugin_info.name)
            self.add_commands_from_plugin(plugin_info.plugin_object)
            plugin_info.plugin_object.attach_bot(self)

    def add_commands_from_plugin(self, plugin):
        methods = inspect.getmembers(plugin, inspect.ismethod)
        for name, method in methods:
            if hasattr(method, "_command"):
                if hasattr(method, "_respond"):
                    self.respond_commands.setdefault(method._event_type, [])
                    self.respond_commands[method._event_type].append((method, method._pattern))
                else:
                    self.listen_commands.setdefault(method._event_type, [])
                    self.listen_commands[method._event_type].append((method, method._pattern))
            if hasattr(method, "_eventfilter"):
                self.event_filters.append(method)

    def get_plugin_manager(self):
        locator = PluginFileLocator(PluginFileAnalyzerWithInfoFile('info_ext', 'plug'))
        plugin_manager = PluginManager(plugin_locator=locator)
        plugin_manager.setPluginPlaces(self.config.PLUGIN_PATHS)

    def get_client(self):
        token = self.config.TOKEN
        client = slackclient.SlackClient(token)
        auth_test = client.api_call('auth.test')
        if not auth_test.get('ok'):
            logger.error("Authentication failed")
            error = auth_test.get('error')
            if error == 'invalid_auth':
                logger.error('Provided API token was invalid')
            elif error == 'account_inactive':
                logger.error('Provided API token is for a deleted user/team')

            sys.exit(-1)
        return client

    def run(self):
        self.client.rtm_connect()
        logger.debug("Started RTM connection")
        # Add username to bot aliases
        self.config.BOT_ALIASES.extend([self.server.username, "<@{}>".format(self.server.login_data["self"]["id"])])

        while True:
            for data in self.client.rtm_read():
                if data.get('ok'):
                    logger.debug("Successful message response")
                    continue
                self.parse_event(data)

    def parse_event(self, data):
        # Don't do anything with messages from myself
        if data.get("user") == self.server.login_data["self"]["id"]:
            return

        # Do event filters first
        if self.event_filters:
            for func in self.event_filters:
                data = func(data)

        if not data:
            return

        regex_fields = {"message": "text",
                        "reaction_added": "reaction",
                        "reaction_removed": "reaction"}

        event_type = data["type"]

        # We want these to be list -copies-
        listen_commands = list(self.listen_commands.get(event_type) or [])
        respond_commands = list(self.respond_commands.get(event_type) or [])

        field = regex_fields.get(event_type)

        respond = False

        # If the event is a message, check if the message starts with an alias for the bot, and remove the alias
        if event_type == "message":
            for alias in self.config.BOT_ALIASES:
                if data["text"].startswith(alias):
                    respond = True
                    data["text"] = data["text"][len(alias):]
                    break
        elif data.get("channel", "").startswith("D"):
            # If we're in a DM, we want to accept ALL commands
            respond = True
            respond_commands.extend(listen_commands)
            # Convert to a set and back to remove duplicate commands
            respond_commands = list(set(respond_commands))

        # Select which list of commands we want to use
        commands = respond_commands if respond else listen_commands
        commands_to_run = []

        # Assemble a list of commands to run, we want to run all the ones that we can
        if commands:
            for function, pattern in commands:
                if field:
                    match = pattern.search(data[field])
                    if match:
                        commands_to_run.append((function, match))
                else:
                    commands_to_run.append((function, False))

        for function, match in commands_to_run:
            logger.debug("Running command {}".format(function.__name__))
            if match:
                function(data, *match.groups())
            else:
                function(data)



def main(config_path=None):
    config = get_config(config_path)
    bot = Bot(config)
    bot.run()


def get_config(config_path):
    if config_path:
        sys.path.insert(0, os.path.dirname(config_path))
    else:
        config_path = os.path.join(os.getcwd(), "config.py")

    if os.path.isfile(config_path):
        logger.debug("Loading config from {}".format(config_path))
        config = __import__(os.path.splitext(os.path.basename(config_path))[0])
    else:
        logger.error('Cannot find config file {}'.format(config_path))
        sys.exit(-1)

    return config
