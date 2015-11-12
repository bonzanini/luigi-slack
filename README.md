luigi-slack
===========

`luigi-slack` adds Slack notifications to Luigi.

Installation
------------

From the cheese shop:

    pip install luigi_slack


From GitHub:

    git clone https://github.com/bonzanini/luigi-slack
    cd luigi-slack
    python setup.py install


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

Example of usage:

```python
import luigi
from luigi_slack import SlackBot, notify

# ...

slacker = SlackBot(token='my-token',
                   channels=['mychannel', 'anotherchannel'])
with notify(slacker):
    luigi.run(main_task_cls=MyTask)
```

--------

Credits: inspired by [luigi-monitor](https://github.com/hudl/luigi-monitor>).
