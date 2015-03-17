from redmine import is_ticket, sanitize, get_issue_subject
import pytest


def line_matrix():
    pre_garbage = [' ', '', 'some question about ',]
    prefixes = ['issue', 'ticket', 'bug', 'Issue', 'TICKET', 'BuG']
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

