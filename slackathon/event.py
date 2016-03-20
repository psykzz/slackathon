from collections import MutableMapping
import logging

logger = logging.getLogger(__name__)

class SlackEvent(MutableMapping):
    def __init__(self, data, client):
        self.data = data
        self.client = client

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value

    def __delitem__(self, item):
        del self.data[item]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def reply(self, message=None, **kwargs):
        channel = self.data.get("channel") or self.data.get("item").get("channel")
        if channel:
            if kwargs:
                self.client.api_call("chat.postMessage",
                                     channel=channel,
                                     text=message,
                                     **kwargs)
            else:
                self.client.rtm_send_message(channel, message)
