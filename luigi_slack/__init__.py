from pkg_resources import get_distribution
from luigi_slack.api import SlackBot, notify

__version__ = get_distribution('luigi_slack').version
