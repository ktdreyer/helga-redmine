import treq
import re
from helga.plugins import match, ResponseNotReady
from helga import log, settings

from twisted.internet import defer

logger = log.getLogger(__name__)

def get_api_key(settings):
    if hasattr(settings, 'REDMINE_API_KEY'):
        logger.debug("REDMINE_API_KEY is set. I will use this key to read private tickets.")
        return settings.REDMINE_API_KEY
    else:
        logger.debug("REDMINE_API_KEY is not set. I can only read public tickets.")
        return None


@defer.inlineCallbacks
def get_issue_subject(ticket_url, api_key=None):
    """
    Find the "subject" string in the JSON data of a ticket.
    :param ticket_url: URL for a ticket
    :param api_key: API secret key (string), or None if you do not want to
                    authenticate to Redmine.
    :returns: twisted.internet.defere.Deferred. When this Deferred fires, it
              will return a "subject" string to its callback.
    """
    api_url = "%s.json" % ticket_url
    request_headers = {}
    if api_key is not None:
        request_headers['X-Redmine-API-Key'] = api_key
    try:
        response = yield treq.get(api_url, headers=request_headers, timeout=5)
        if response.code != 200:
            defer.returnValue('could not read subject, HTTP code %i' %
                              response.code)
        else:
            content = yield treq.json_content(response)
            defer.returnValue(content['issue']['subject'])
    except Exception, e:
        # For example, if treq.get() timed out, or if treq.json_content() could
        # not parse the JSON, etc.
        defer.returnValue('could not read subject, %s' % e.message)

def send_message(subject, client, channel, nick, ticket_url):
    """
    Send a message to an IRC/XMPP channel about a Redmine ticket.
    """
    msg = "%s might be talking about %s [%s]" % (nick, ticket_url, subject)
    client.msg(channel, msg)

ticket_regex = re.compile(
   r'.*(?:issue|ticket|bug|redmine)+\s+#?([0-9]+)', re.IGNORECASE
)

@match(ticket_regex, priority=0)
def redmine(client, channel, nick, message, matches):
    """
    Match possible Redmine tickets, return links and subject info
    """
    ticket_number = matches[0]

    try:
        ticket_url = settings.REDMINE_URL % {'ticket': ticket_number}
    except AttributeError:
        return 'Please configure REDMINE_URL to point to your tracker.'

    api_key = get_api_key(settings)

    d = get_issue_subject(ticket_url, api_key)
    d.addCallback(send_message, client, channel, nick, ticket_url)

    raise ResponseNotReady
