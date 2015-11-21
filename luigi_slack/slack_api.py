import json
from slackclient import SlackClient
import logging

class ChannelNotFoundError(Exception):
    pass

class SlackAPI(object):
    
    def __init__(self, token, username='Luigi-slack Bot'):
        self.client = SlackClient(token)
        self._all_channels = self._get_channels()
        self.username = username

    def _get_channels(self):
        res = self.client.api_call('channels.list')
        _channels = json.loads(res.decode())
        _parsed_channels = _channels.get('channels', None)
        if _parsed_channels is None:
            raise Exception("Could not get Slack channels. Are you sure your token is correct?")
        return _parsed_channels

    def get_channels(self, reload_channels=False):
        if not self._all_channels or reload_channels:
            self._all_channels = self._get_channels()
        return self._all_channels

    def channel_name_to_id(self, channel_name):
        for channel in self._all_channels:
            if channel['name'] == channel_name:
                return channel['id']
        raise ChannelNotFoundError("Channel {} not in the list of available channels".format(channel_name))

    def bulk_message(self, message, post_to=[]):
        for channel in post_to:
            if not channel.startswith('@'):
                channel = self.channel_name_to_id(channel)
            logging.debug("Posting message to {}".format(channel))
            self.client.api_call('chat.postMessage',
                                 text=message,
                                 channel=channel,
                                 username=self.username)
        return True
