import requests
import re
from helga.plugins import match
from helga import log, settings

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
       r'(.*)(issue|ticket|bug|redmine)+\s+(#[0-9]+|[0-9]+)', re.IGNORECASE
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

def get_ticket_response(api_url, api_key):
    if api_key:
        request_headers = {'X-Redmine-API-Key': api_key}
    else:
        request_headers = {}
    return requests.get(api_url, headers=request_headers)


def get_issue_subject(response):
    """Find the "subject" string in the JSON data of python-requests' response
    object."""
    try:
        result = response.json()
    except ValueError as err:
        result = {}
        logger.error("couldn't access that URL. response was %s: %s" % (response.status_code, err))

    try:
        return result['issue']['subject']
    except KeyError:
        return 'unable to read subject'


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
    api_key = get_api_key(settings)
    response = get_ticket_response(api_url, api_key)
    subject = get_issue_subject(response)

    return "%s might be talking about %s [%s]" % (nick, ticket_url, subject)
