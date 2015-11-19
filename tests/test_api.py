import sys
import unittest
from unittest import mock
import luigi
import luigi_slack.api
from luigi_slack.api import SlackBot
from luigi_slack.api import notify
from luigi_slack.events import *

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
        """Test SlackAPI is called by send_notification()"""
        self.bot.send_notification()

    def test_events_not_list(self):
        """Raise a ValueError if events is not a list"""
        with self.assertRaises(ValueError):
            bot = SlackBot(self.token, events='FOOBAR')
            bot = SlackBot(self.token, events=123)
            bot = SlackBot(self.token, events=None)
            bot = SlackBot(self.token, events=True)

    def test_set_handlers_valid(self):
        """Test set_handlers() for valid events"""
        bot = SlackBot(self.token, events=[SUCCESS, FAILURE])
        bot.set_handlers()

    def test_set_handlers_invalid(self):
        """Test set_handlers for invalid events"""
        bot = SlackBot(self.token, events=['THIS-IS-NOT-A-VALID-EVENT'])
        with self.assertRaises(ValueError):
            bot.set_handlers()


class TestEvents(unittest.TestCase):

    def test_event_label(self):
        """Test event labels for output"""
        fixtures = {
            'SUCCESS': '*Success*',
            'FAILURE': '*Failure*',
            'MISSING': '*Missing*',
        }
        for event, expected in fixtures.items():
            self.assertEqual(event_label(event), expected)


class TestHandlers(unittest.TestCase):

    def setUp(self):
        self.patcher = mock.patch('luigi_slack.api.SlackAPI') 
        self.mock_SlackAPI = self.patcher.start()
        self.token = 'dummy-token'
        self.channels = ['channel1']

    def tearDown(self):
        self.patcher.stop()

    def test_success(self):
        """Test successful task if queued"""
        bot = SlackBot(self.token, events=[SUCCESS], channels=self.channels)
        bot.set_handlers()
        task = luigi.Task()
        self.assertEqual(len(bot.event_queue.get(SUCCESS, [])), 0)
        task.trigger_event(luigi.event.Event.SUCCESS, task)
        self.assertEqual(len(bot.event_queue.get(SUCCESS)), 1)

    def test_success_empties_queue(self):
        """Test success event empties the failure queue"""
        bot = SlackBot(self.token, events=[SUCCESS, FAILURE], channels=self.channels)
        bot.set_handlers()
        task1 = luigi.Task() # task1 and task2 have the same task_id
        task2 = luigi.Task()
        self.assertEqual(len(bot.event_queue.get(FAILURE, [])), 0)
        task2.trigger_event(luigi.event.Event.FAILURE, task2, Exception())
        self.assertEqual(len(bot.event_queue.get(FAILURE)), 1)
        task1.trigger_event(luigi.event.Event.SUCCESS, task1)
        self.assertEqual(len(bot.event_queue.get(FAILURE)), 0)

    def test_different_task_doesnt_empty_queue(self):
        """Test a successful task doesn't empty queue with different task"""
        class CustomTask(luigi.Task):
            pass
        bot = SlackBot(self.token, events=[SUCCESS, FAILURE], channels=self.channels)
        bot.set_handlers()
        task1 = luigi.Task() # task1 and task2 have different task_id
        task2 = CustomTask()
        self.assertEqual(len(bot.event_queue.get(FAILURE, [])), 0)
        task2.trigger_event(luigi.event.Event.FAILURE, task2, Exception())
        self.assertEqual(len(bot.event_queue.get(FAILURE)), 1)
        task1.trigger_event(luigi.event.Event.SUCCESS, task1)
        self.assertEqual(len(bot.event_queue.get(FAILURE)), 1)

    def test_start(self):
        """Test start event adds task in queue"""
        bot = SlackBot(self.token, events=[START], channels=self.channels)
        bot.set_handlers()
        task = luigi.Task()
        self.assertEqual(len(bot.event_queue.get(START, [])), 0)
        task.trigger_event(luigi.event.Event.START, task)
        self.assertEqual(len(bot.event_queue.get(START)), 1)

    def test_failure(self):
        """Test failure event adds task in queue"""
        bot = SlackBot(self.token, events=[FAILURE], channels=self.channels)
        bot.set_handlers()
        task = luigi.Task()
        self.assertEqual(len(bot.event_queue.get(FAILURE, [])), 0)
        task.trigger_event(luigi.event.Event.FAILURE, task, Exception())
        self.assertEqual(len(bot.event_queue.get(FAILURE)), 1)

    def test_missing(self):
        """Test missing dependency event adds task in queue"""
        bot = SlackBot(self.token, events=[MISSING], channels=self.channels)
        bot.set_handlers()
        task = luigi.Task()
        self.assertEqual(len(bot.event_queue.get(MISSING, [])), 0)
        task.trigger_event(luigi.event.Event.DEPENDENCY_MISSING, task)
        self.assertEqual(len(bot.event_queue.get(MISSING)), 1)

    def test_event_not_implemented(self):
        """Test processing time event is not implemented yet"""
        bot = SlackBot(self.token, events=[PROCESSING_TIME], channels=self.channels)
        bot.set_handlers()
        task = luigi.Task()
        self.assertRaises(NotImplementedError, task.trigger_event(luigi.event.Event.PROCESSING_TIME, task))


class MockSlackBot(object):
    def set_handlers(self):
        return True
    def send_notification(self):
        return True


class TestNotify(unittest.TestCase):

    def test_notify(self):
        """Test notify() performs pre/post operations"""
        slacker = MockSlackBot()
        some_test = False
        with notify(slacker):
            some_test = True
        self.assertTrue(some_test)
