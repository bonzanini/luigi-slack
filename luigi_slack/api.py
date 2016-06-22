import os
import logging
import inspect
from contextlib import contextmanager
from collections import defaultdict
import luigi
from luigi_slack.slack_api import SlackAPI
from luigi_slack.events import SUCCESS
from luigi_slack.events import MISSING
from luigi_slack.events import FAILURE
from luigi_slack.events import START
from luigi_slack.events import PROCESSING_TIME
from luigi_slack.events import event_label

log = logging.getLogger('luigi_slack')
log.setLevel(logging.DEBUG)


class SlackMessage(object):

    def __init__(self, title=None, fields={}, success=None):
        self.title = title
        self.fields = fields
        self.success = success


class SlackBot(object):

    def __init__(self,
                 token,
                 channels=[],
                 events=[FAILURE],
                 max_events=5,
                 username='Luigi-slack Bot',
                 task_representation=str,
                 print_env=[]):
        if not isinstance(events, list):
            raise ValueError('events must be a list, {} given'.format(type(events)))
        if not channels:
            log.info('SlackBot(channels=[]): notifications are not sent')
        self.events = events
        self._events_to_handle = self.events + [START]
        self.client = SlackAPI(token, username)
        self.channels = channels
        self.max_events = max_events
        self.event_queue = defaultdict(list)
        self.task_repr = task_representation
        self._print_env = print_env

    def send_notification(self):
        message = self._format_message()
        post_to = self.channels
        if message:
            self.client.bulk_message(message, post_to)
        return True

    def set_handlers(self):
        self._init_handlers()
        for event in self._events_to_handle:
            if event not in self._event_handlers:
                raise ValueError("{} is not a valid event type".format(event))
            handler = self._event_handlers[event]['luigi_handler']
            function = self._event_handlers[event]['function']
            luigi.Task.event_handler(handler)(function)
        return True

    def _init_handlers(self):
        self._event_handlers = {
            SUCCESS: {
                'luigi_handler': luigi.Event.SUCCESS,
                'function': self._success
            },
            FAILURE: {
                'luigi_handler': luigi.Event.FAILURE,
                'function': self._failure
            },
            START: {
                'luigi_handler': luigi.Event.START,
                'function': self._start
            },
            MISSING: {
                'luigi_handler': luigi.Event.DEPENDENCY_MISSING,
                'function': self._missing
            },
            PROCESSING_TIME: {
                'luigi_handler': luigi.Event.PROCESSING_TIME,
                'function': self._processing_time
            }
        }

    def _success(self, task):
        task = self.task_repr(task)
        self.event_queue[FAILURE] = [fail for fail in self.event_queue[FAILURE] if task != fail['task']]
        self.event_queue[MISSING] = [miss for miss in self.event_queue[MISSING] if task != miss]
        self.event_queue[SUCCESS].append(task)

    def _failure(self, task, exception):
        task = self.task_repr(task)
        failure = {'task': task, 'exception': str(exception)}
        self.event_queue[FAILURE].append(failure)

    def _missing(self, task):
        task = self.task_repr(task)
        self.event_queue[MISSING].append(task)

    def _start(self, task):
        task = self.task_repr(task)
        self.event_queue[START].append(task)

    def _processing_time(self, task):
        raise NotImplementedError
        # task = self.task_repr(task)
        # self.event_queue[PROCESSING_TIME].append(task)

    def _format_message(self):
        job = os.path.basename(inspect.stack()[-1][1])
        title = "*Status report for {}*".format(job)
        if self._only_success():
            if SUCCESS in self.events:
                messages = {event_label(SUCCESS): ["Job ran successfully!"]}
                success = True
            else:
                return None
        else:
            messages = self._event_messages()
            success = False
        if self._print_env:
            env_to_print = ["{}={}".format(env_var, os.environ.get(env_var, ''))
                            for env_var in self._print_env]
            messages['Environment'] = env_to_print
        return SlackMessage(title=title, fields=messages, success=success)

    def _only_success(self):
        return len(self.event_queue[SUCCESS]) == len(self.event_queue[START])

    def _event_messages(self):
        messages = {}
        for event_type in self.events:
            if event_type in self.event_queue:
                label = event_label(event_type)
                if not self.event_queue[event_type]:
                    messages[label] = ['none']
                elif len(self.event_queue[event_type]) > self.max_events:
                    messages[label] = ["more than {} events, check logs.".format(self.max_events)]
                else:
                    messages[label] = []
                    for event in self.event_queue[event_type]:
                        try:
                            # only "failure" is a dict
                            msg = "Task: {}; Exception: {}".format(event['task'], event['exception'])
                            messages[label].append("Task: {}; Exception: {}".format(event['task'], event['exception']))
                        except TypeError:
                            # all the other events are str
                            messages[label].append(event)
        return messages


@contextmanager
def notify(slacker):
    slacker.set_handlers()
    yield
    slacker.send_notification()
