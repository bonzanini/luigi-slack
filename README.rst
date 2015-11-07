luigi-slack
===========

`luigi-slack` adds Slack notifications to Luigi.


Current status
--------------

At the moment this is a proof-of-concept, version 0.1

This is **experimental** and the API could change drastically


Features
--------

Roadmap to version 1.0

- Python 3
- Configurable notifications on different events
- Straightforward interface


Usage
-----

Example of usage::

    from luigi_slack import SlackBot, notify

    # ...

    slacker = SlackBot(token='my-token',
                       channels=['mychannel', 'anotherchannel'],
                       events=['SUCCESS', 'FAILURE'])
    with notify(slacker):
        luigi.run(main_task_cls=MyTask)