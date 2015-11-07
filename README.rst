luigi-slack
===========

`luigi-slack` adds Slack notifications to Luigi.

Features:

- Python 3
- Configurable notifications on different events
- Straightforward interface

Current status: PoC, experimental

Example of usage::

    from luigi_slack import SlackBot, notify

    # ...

    slacker = SlackBot(token='my-token',
                       channels=['mychannel', 'anotherchannel'],
                       events=['SUCCESS', 'FAILURE'])
    with notify(slacker):
        luigi.run(main_task_cls=MyTask)