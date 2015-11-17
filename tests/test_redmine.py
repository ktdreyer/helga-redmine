from redmine import is_ticket, sanitize, get_ticket_response, get_api_key, get_issue_subject
import pytest
import httpretty
import json


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
        assert is_ticket(line)

    @pytest.mark.parametrize('line', fail_line_matrix())
    def test_does_not_match(self, line):
        assert is_ticket(line) is None



def match_matrix():
    matches = ['1234', '#1234']
    prefixes = ['', ' ']
    suffixes = ['', ' ']
    lines = []

    for match in matches:
        for prefix in prefixes:
            for suffix in suffixes:
                lines.append(
                    ['', '%s%s%s' % (prefix, match, suffix)]
                )
    return lines



class TestSanitize(object):

    @pytest.mark.parametrize('match', match_matrix())
    def test_sanitizes(self, match):
        assert sanitize(match) == '1234'


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


class FakeResponse(object):
    pass


class TestGetIssueSubject(object):

    def test_get_correct_subject(self):
        response = FakeResponse()
        response.json = lambda: {'issue':{'subject': 'some issue subject'}}
        result = get_issue_subject(response)
        assert result == 'some issue subject'

    def test_get_fallback_subject(self):
        response = FakeResponse()
        response.json = lambda: {}
        result = get_issue_subject(response)
        assert result == 'unable to read subject'

class TestAPIKeySubject(object):

    api_url = 'http://tracker.example.com/issues/1234.json'

    def request_callback(self, request, uri, headers):
        if 'X-Redmine-API-Key' in request.headers:
            payload = {'issue':{'subject': 'some issue subject'}}
            return (200, headers, json.dumps(payload))
        else:
            return (401, headers, 'Unauthorized')

    @httpretty.activate
    def test_has_x_redmine_api_key(self):
        httpretty.register_uri(
            httpretty.GET, self.api_url,
            body=self.request_callback)

        response = get_ticket_response(self.api_url, '123deadbeef')
        assert response.status_code == 200

        result = get_issue_subject(response)
        assert result == 'some issue subject'

    @httpretty.activate
    def test_has_no_x_redmine_api_key(self):
        httpretty.register_uri(
            httpretty.GET, self.api_url,
            body=self.request_callback)
        response = get_ticket_response(self.api_url, None)
        assert response.status_code == 401

        result = get_issue_subject(response)
        assert result == 'unable to read subject'
