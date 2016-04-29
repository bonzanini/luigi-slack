import json
from slackclient import SlackClient
import logging

log = logging.getLogger('luigi_slack')
log.setLevel(logging.DEBUG)


class ChannelNotFoundError(Exception):
    pass


class ChannelListNotLoadedError(Exception):
    pass


class SlackAPI(object):

    def __init__(self, token, username='Luigi-slack Bot'):
        self.client = SlackClient(token)
        self._all_channels = self._get_channels()
        self.username = username

    def _get_channels(self):
        response = self.client.api_call('channels.list')
        if not response['ok']:
            raise ChannelListNotLoadedError("Error while loading channels: {}".format(response['error']))
        _parsed_channels = response.get('channels', [])
        if not _parsed_channels:
            raise ChannelListNotLoadedError("Channel list is empty")
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
        log.debug("Posting bulk message={}".format(message.title))
        for channel in post_to:
            if not channel.startswith('@'):
                channel = self.channel_name_to_id(channel)
            log.debug("Posting message to {}".format(channel))
            success_color = 'good' if message.success else 'danger'
            attachments = {'color': success_color}
            fields = []
            for label, msg in message.fields.items():
                fields.append({'title': label, 'value': "\n".join(msg), 'short': False})
            attachments['fields'] = fields
            attachments = json.dumps([attachments])
            response = self.client.api_call('chat.postMessage',
                                            text=message.title,
                                            attachments=attachments,
                                            channel=channel,
                                            username=self.username)
            log.debug(response)
            if not response['ok']:
                log.debug("Error while posting message to {}: {}".format(channel, response['error']))
        return True
