import requests
import re
from helga.plugins import match
from helga import log, settings

logger = log.getLogger(__name__)


def is_ticket(message):
   regex = re.compile(
       r'(.*)(issue|ticket|bug)+\s+(#[0-9]+|[0-9]+)'
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


@match(is_ticket, priority=0)
def redmine(client, channel, nick, message, matches):
    """
    Match possible Redmine tickets, return links and subject info
    """
    ticket_number = sanitize(matches.groups())

    if not ticket_number:
        logger.warning('I could not determine the right ticket from matches: %s' % matches.groups())

    ticket_url = settings.REDMINE_URL % {'ticket': ticket_number}
    api_url = "%s.json" % ticket_url
    response = requests.get(api_url)
    try:
        result = response.json()
    except ValueError as err:
        return "couldn't access that URL. response was %s: %s" % (response.status_code, err)

    try:
        subject = result['issue']['subject']
    except KeyError:
        subject = '[no subject]'

    return "%s might be talking about %s [%s]" % (nick, ticket_url, subject)
