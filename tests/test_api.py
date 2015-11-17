import unittest
from unittest import mock
import luigi_slack.api
from luigi_slack.api import SlackBot
from luigi_slack.events import *

# class MockSlackAPI(object):

#     def bulk_message(self, message, post_to):
#         pass

class TestSlackBot(unittest.TestCase):

    def setUp(self):
        self.patcher = mock.patch('luigi_slack.api.SlackAPI') 
        self.mock_SlackAPI = self.patcher.start()
        self.token = 'dummy-token'
        self.channels = ['channel1', 'channel2']
        self.bot = SlackBot(self.token, channels=self.channels)

    def tearDown(self):
        self.patcher.stop()

    def test_send_notification(self):
        self.bot.send_notification()

    def test_events_not_list(self):
        """Raise a ValueError if events is not a list"""
        with self.assertRaises(ValueError):
            bot = SlackBot(self.token, events='FOOBAR')
            bot = SlackBot(self.token, events=123)
            bot = SlackBot(self.token, events=None)
            bot = SlackBot(self.token, events=True)

    def test_set_handlers_valid(self):
        bot = SlackBot(self.token, events=[SUCCESS, FAILURE])
        bot.set_handlers()

    def test_set_handlers_invalid(self):
        bot = SlackBot(self.token, events=['THIS-IS-NOT-A-VALID-EVENT'])
        with self.assertRaises(ValueError):
            bot.set_handlers()

class TestEvents(unittest.TestCase):

    def test_event_label(self):
        fixtures = {
            'SUCCESS': '*Success*',
            'FAILURE': '*Failure*',
            'MISSING': '*Missing*',
        }
        for event, expected in fixtures.items():
            self.assertEqual(event_label(event), expected)