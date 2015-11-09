import os
import logging
import inspect
from contextlib import contextmanager
from collections import defaultdict
from slackclient import SlackClient
import luigi
from luigi_slack.slack_api import SlackAPI
from luigi_slack import events

class SlackBot(object):

    def __init__(self,
                 token,
                 channels=[],
                 events=[events.FAILURE, events.SUCCESS]):
        if not isinstance(events, list):
            raise ValueError('events must be a list, {} given'.format(type(events)))
        if not channels:
            logging.info('channels=[], notifications are not sent')
        self.events = events
        self.client = SlackAPI(token)
        available_channels = self.client.get_channels()
        self.channels = channels
        self.event_queue = defaultdict(list)    

    def send_notification(self):
        message = self._format_message()
        self.client.bulk_message(message, self.channels)
        return True

    def set_handlers(self):
        for event in self.events:
            if event not in _event_handlers:
                raise ValueError("{} is not a valid event".format(event))
            handler = _event_handlers[event]['luigi_handler']
            function = _event_handlers[event]['function']
            luigi.Task.event_handler(handler)(function)
        return True

    def _success(self, task):
        task = str(task)
        self.event_queue['Failure'] = [fail for fail in self.event_queue['Failure'] if task != fail['task']]
        self.event_queue['Missing'] = [miss for miss in self.event_queue['Missing'] if task != miss]
        self.event_queue['Start'] = [start for start in self.event_queue['Start'] if task != start]

    def _failure(self, task: luigi.Task, exception: Exception):
        task = str(task)
        failure = {'task': task, 'exception': str(exception)}
        self.event_queue['Failure'].append(failure)

    def _missing(self, task: luigi.Task):
        task = str(task)
        self.event_queue['Missing'].append(task)

    def _start(self, task: luigi.Task):
        task = str(task)
        self.event_queue['Start'].append(task)

    def _format_message(self):
        job = os.path.basename(inspect.stack()[-1][1])
        text = ["Status report for {}".format(job)]
        if 'Failure' in self.event_queue:
            text.append("*Failures:*")
            if len(self.event_queue['Failure']) > 5:
                text.append("More than 5 failures. Please check logs.")
            else:
                for failure in self.event_queue['Failure']:
                    text.append("Task: {}; Exception: {}".format(failure['task'], failure['exception']))
        if 'Missing' in self.event_queue:
            text.append("*Tasks with missing dependencies:*")
            if len(self.event_queue['Missing']) > 5:
                text.append("More than 5 tasks with missing dependencies. Please check logs.")
            else:
                for missing in self.event_queue['Missing']:
                    text.append(missing)
        if len(text) == 1:
            text.append("Job ran successfully!")
        text = "\n".join(text)
        return text


_event_handlers = {
    events.SUCCESS: {
        'luigi_handler': luigi.Event.SUCCESS,
        'function': SlackBot._success
    },
    events.FAILURE: {
        'luigi_handler': luigi.Event.FAILURE,
        'function': SlackBot._failure
    },
    events.START: {
        'luigi_handler': luigi.Event.START,
        'function': SlackBot._start
    }
}


@contextmanager
def notify(slacker):
    slacker.set_handlers()
    yield
    slacker.send_notification()
