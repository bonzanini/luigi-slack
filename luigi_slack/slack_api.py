import json
from slackclient import SlackClient

class SlackBotConf(object):
    def __init__(self):
        self.username = 'Luigi-slack Bot'

class SlackAPI(object):
    
    def __init__(self, token, bot_conf=SlackBotConf()):
        self.client = SlackClient(token)
        self._all_channels = self._get_channels()
        self.bot = bot_conf

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

    def channel_name_to_id(self, names):
        name_to_id = []
        for name in names:
            for channel in self._all_channels:
                if channel['name'] == name:
                    name_to_id.append({'name': channel['name'], 'id': channel['id']})
        return name_to_id

    def bulk_message(self, message, post_to=[]):
        channel_map = self.channel_name_to_id(post_to)
        for channel in channel_map:
            self.client.api_call('chat.postMessage',
                                 text=message,
                                 channel=channel['id'],
                                 username=self.bot.username)
        return True
