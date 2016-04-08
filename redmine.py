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


def is_ticket(message):
   regex = re.compile(
       r'(.*)(issue|ticket|bug|redmine)+\s+#?([0-9]+)', re.IGNORECASE
   )
   return regex.match(message)


def sanitize(match):
    """
    this function sanitizes the match from a ``regex.match(phrase)``
    call to return the ticket id only.
    """
    if not match:
        return ''
    ticket_id = match[-1]  # Always the last one in the group
    ticket_id = ticket_id.strip()  # probably not necessary?
    return ticket_id.strip('#')

@defer.inlineCallbacks
def get_issue_subject(api_url, api_key=None):
    """
    Find the "subject" string in the JSON data of an api_url.
    :param api_url: JSON API URL to GET via HTTP.
    :param api_key: API secret key (string), or None if you do not want to
                    authenticate to Redmine.
    :returns: twisted.internet.defere.Deferred. When this Deferred fires, it
              will return a "subject" string to its callback.
    """
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

@match(is_ticket, priority=0)
def redmine(client, channel, nick, message, matches):
    """
    Match possible Redmine tickets, return links and subject info
    """
    ticket_number = sanitize(matches.groups())

    if not ticket_number:
        logger.warning('I could not determine the right ticket from matches: %s' % matches.groups())

    try:
        ticket_url = settings.REDMINE_URL % {'ticket': ticket_number}
    except AttributeError:
        return 'Please configure REDMINE_URL to point to your tracker.'

    api_url = "%s.json" % ticket_url
    api_key = get_api_key(settings)

    d = get_issue_subject(api_url, api_key)
    d.addCallback(send_message, client, channel, nick, ticket_url)

    raise ResponseNotReady
