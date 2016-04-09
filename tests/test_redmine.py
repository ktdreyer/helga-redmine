from redmine import ticket_regex, get_issue_subject, construct_message, send_message, get_api_key
import pytest
import re
import json
from treq.testing import StubTreq
from twisted.web.resource import Resource


def line_matrix():
    pre_garbage = [' ', '', 'some question about ',]
    prefixes = ['issue', 'ticket', 'bug', 'Issue', 'TICKET', 'BuG', 'redmine']
    numbers = ['#123467890', '1234567890']
    garbage = ['?', ' ', '.', '!', '..', '...']
    lines = []

    for pre in pre_garbage:
        for prefix in prefixes:
            for number in numbers:
                for g in garbage:
                    lines.append('%s%s %s%s' % (
                        pre, prefix, number, g
                        )
                    )
    return lines

def fail_line_matrix():
    pre_garbage = [' ', '', 'some question about ',]
    pre_prefixes = ['', ' ', 'f']
    prefixes = ['issues', 'tickets', 'bugs', 'issue', 'ticket', 'bug']
    numbers = ['#G123467890', 'F1234567890']
    garbage = ['?', ' ', '.', '!', '..', '...']
    lines = []

    for pre in pre_garbage:
        for pre_prefix in pre_prefixes:
            for prefix in prefixes:
                for number in numbers:
                    for g in garbage:
                        lines.append('%s%s%s %s%s' % (
                            pre, pre_prefix, prefix, number, g
                            )
                        )
    return lines



class TestIsTicket(object):

    @pytest.mark.parametrize('line', line_matrix())
    def test_matches(self, line):
        assert len(re.findall(ticket_regex, line)) > 0

    @pytest.mark.parametrize('line', fail_line_matrix())
    def test_does_not_match(self, line):
        assert re.findall(ticket_regex, line) == []


class FakeClient(object):
    """
    Fake Helga client (eg IRC or XMPP) that simply saves the last
    message sent.
    """
    def msg(self, channel, msg):
        self.last_message = (channel, msg)


class TestSendMessage(object):
    def test_send_message(self):
        subject = 'some issue subject'
        ticket_url = 'http://example.com/issues/1'
        urls_and_subjects = [(ticket_url, subject)]
        client = FakeClient()
        channel = '#bots'
        nick = 'ktdreyer'
        # Send the message using our fake client
        send_message(urls_and_subjects, client, channel, nick)
        expected = ('ktdreyer might be talking about '
                    'http://example.com/issues/1 [some issue subject]')
        assert client.last_message == (channel, expected)


class TestConstructMessage(object):
    def test_construct_message(self):
        ticket_url = 'http://example.com/issues/1'
        subject = 'some issue subject'
        nick = 'ktdreyer'
        result = construct_message([(ticket_url, subject)], nick)
        expected = ('ktdreyer might be talking about '
                    'http://example.com/issues/1 [some issue subject]')
        assert result == expected

    def test_two_tickets(self):
        urls_and_subjects = []
        urls_and_subjects.append(('http://example.com/issues/1', 'subj 1'))
        urls_and_subjects.append(('http://example.com/issues/2', 'subj 2'))
        nick = 'ktdreyer'
        result = construct_message(urls_and_subjects, nick)
        expected = ('ktdreyer might be talking about '
                    'http://example.com/issues/1 [subj 1] and '
                    'http://example.com/issues/2 [subj 2]')
        assert result == expected

    def test_four_tickets(self):
        """ Verify that commas "," and "and" get put in the right places. """
        urls_and_subjects = []
        urls_and_subjects.append(('http://example.com/issues/1', 'subj 1'))
        urls_and_subjects.append(('http://example.com/issues/2', 'subj 2'))
        urls_and_subjects.append(('http://example.com/issues/3', 'subj 3'))
        urls_and_subjects.append(('http://example.com/issues/4', 'subj 4'))
        nick = 'ktdreyer'
        result = construct_message(urls_and_subjects, nick)
        expected = ('ktdreyer might be talking about '
                    'http://example.com/issues/1 [subj 1], '
                    'http://example.com/issues/2 [subj 2], '
                    'http://example.com/issues/3 [subj 3] and '
                    'http://example.com/issues/4 [subj 4]')
        assert result == expected


class FakeSettings(object):
    pass


class TestGetAPIKey(object):
    def test_get_correct_api_key(self):
        settings = FakeSettings()
        settings.REDMINE_API_KEY = '1a64a94f14d8598de9211753a1450dbb'
        result = get_api_key(settings)
        assert result == '1a64a94f14d8598de9211753a1450dbb'

    def test_get_missing_api_key(self):
        settings = FakeSettings()
        result = get_api_key(settings)
        assert result == None

class _TicketTestResource(Resource):
    """
    A twisted.web.resource.Resource that represents a private Redmine ticket.
    If the user fails to supply an API key of "abc123", we return an HTTP 401
    Unauthorized response. If the user supplies the proper API key, then we
    return the valid JSON data for the ticket.
    """
    isLeaf = True

    def render(self, request):
        if request.getHeader('X-Redmine-API-Key') == 'abc123':
            request.setResponseCode(200)
            payload = {'issue': {'subject': 'some issue subject'}}
            return json.dumps(payload).encode('utf-8')
        else:
            request.setResponseCode(401)
            return b'denied'

class TestGetIssueSubject(object):

    @pytest.inlineCallbacks
    def test_get_denied_subject(self, monkeypatch):
        monkeypatch.setattr('redmine.treq', StubTreq(_TicketTestResource()))
        ticket_url = 'http://example.com/issues/123'
        result = yield get_issue_subject(ticket_url)
        assert result == (ticket_url, 'could not read subject, HTTP code 401')

    @pytest.inlineCallbacks
    def test_get_correct_subject(self, monkeypatch):
        monkeypatch.setattr('redmine.treq', StubTreq(_TicketTestResource()))
        ticket_url = 'http://example.com/issues/123'
        api_key = 'abc123'
        result = yield get_issue_subject(ticket_url, api_key)
        assert result == (ticket_url, 'some issue subject')
