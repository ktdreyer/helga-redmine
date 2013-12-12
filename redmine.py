import requests
from helga.plugins import match
from helga import log, settings

logger = log.getLogger(__name__)


@match(r'(.*)(issue|ticket|bug)+\s+(#[0-9]+|[0-9]+)($|\s+)', priority=0)
def redmine(client, channel, nick, message, matches):
    """
    Match possible Redmine tickets, return links and subject info
    """
    ticket_number = matches[0][-2].replace('#', '')

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
