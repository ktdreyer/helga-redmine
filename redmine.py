import requests
from helga.plugins import match


@match(r'(.*)(issue|ticket|bug)+\s+(#[0-9]+|[0-9]+)($|\s+)', priority=0)
def redmine(client, channel, nick, message, matches):
    """
    Match possible Redmine tickets, return links and subject info
    """
    ticket_number = matches[-2].replace('#', '')

    ticket_url = settings.REDMINE_URL % {'ticket': ticket_number}
    api_url = "%s.json" % url
    result = requests.get(api_url).json()

    try:
        subject = result['issue']['subject']
    except KeyError:
        subject = '[no subject]'

    subject = self.get_subject(ticket_url)
    return "%s might be talking about %s [%s]" % (nick, ticket_url, subject)
