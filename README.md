luigi-slack
===========

[![PyPI version](https://badge.fury.io/py/luigi-slack.svg)](https://badge.fury.io/py/luigi-slack)

`luigi-slack` adds Slack notifications to Luigi.


Installation
------------

Install from the PyPI:

    pip install luigi_slack

Bleeding edge version from GitHub:

    git clone https://github.com/bonzanini/luigi-slack
    cd luigi-slack
    python setup.py install


Features
--------

At the moment this is a proof-of-concept, version 0.1, and it should be considered **experimental**.

Features:

- Developed for Python 3.4
- Support for Python 2 is best-effort (PR welcome)
- Configurable notifications on different events
- Notifications on channels and to specific user via direct message
- Straightforward interface


Usage
-----

Example of usage:

```python
import luigi
from luigi_slack import SlackBot, notify

# ...

slacker = SlackBot(token='my-token',
                   channels=['my_channel', '@my_username'])
with notify(slacker):
    luigi.run(main_task_cls=MyTask)
```

Notice: channel names don't include the initial `#`, while user names do include the initial `@`.


SlackBot Configuration
----------------------

`SlackBot` takes a number of arguments, but only the token is mandatory. You can customise the SlackBot behaviour with the following arguments:

- channels: list of channels/usernames you want to notify (default=[])
- events: list of events to track, as defined in `luigi_slack.events` (default=[FAILURE])
- max_events: max number of events of the same type displayed, before a "please check logs" message is given (default=5)
- username: the screen name of your bot (default='Luigi-slack Bot')
- as_user: true to post the message as the authenticated user (default=False). When true the argument username is ignored.
- task_representation: the function used to give a string representation of the task (default=str)
- print_env: list of environment variables to include in the notification (default=[]). Useful when running multiple pipelines/environments and sending the notification in a single Slack channel.

[Blog post](http://marcobonzanini.com/2015/11/21/adding-slack-notifications-to-a-luigi-pipeline-in-python/) with a more verbose description of this package.


Contributions
-------------

- [@amarco90](https://github.com/amarco90)
- [@arsenyinfo](https://github.com/arsenyinfo)
- [@saxelsen89](https://github.com/saxelsen89)


--------

Credits: inspired by [luigi-monitor](https://github.com/hudl/luigi-monitor).
