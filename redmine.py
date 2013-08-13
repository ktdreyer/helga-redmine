import random

import smokesignal

from helga import settings
from helga.db import db
from helga.extensions.base import (CommandExtension,
                                   ContextualExtension)
from helga.log import setup_logger


logger = setup_logger(__name__)


class RedmineExtension(CommandExtension, ContextualExtension):

    NAME = 'redmine'

    usage = ''

    allow_many = True

    def __init__(self, *args, **kwargs):
        self.redmine_pats = set()

        # Hack for le instance callbacks
        @smokesignal.on('signon')
        def callback():
            if db is not None:
                self._init_patterns()

        super(RedmineExtension, self).__init__(*args, **kwargs)

    @property
    def context(self):
        # This should not look for URLs. Optionally match url type
        return r'(.*)(issue|ticket|bug)+\s+(#[0-9]+|[0-9]+)($|\s+)'

    def _init_patterns(self):
        return

    def transform_match(self, match):
        ticket_number = match[-2].replace('#', '')

        return settings.REDMINE_URL % {'ticket': ticket_number}

    def handle_message(self, opts, message):
        if opts['add_re']:
            message.response = self.add_re(opts['<pattern>'])
        elif opts['remove_re']:
            message.response = self.remove_re(opts['<pattern>'])

    def add_re(self, pattern):
        if pattern not in self.redmine_pats:
            logger.info('Adding new redmine ticket RE: %s' % pattern)

            self.redmine_pats.add(pattern)
            re_doc = {'re': pattern}

            # Store in DB
            if not db.redmine.find(re_doc).count():
                db.redmine.insert(re_doc)
        else:
            logger.info('redmine ticket RE already exists: %s' % pattern)

        return '%(nick)s, ' + random.choice(self.add_acks)

    def remove_re(self, pattern):
        logger.info('Removing redmine ticket RE: %s' % pattern)
        self.redmine_pats.discard(pattern)
        db.redmine.remove({'re': pattern})

        return '%(nick)s, ' + random.choice(self.delete_acks)

    def process(self, message):
        # Try to contextualize
        self.contextualize(message)

        if message.has_response:
            return

        # Try to handle commands
        opts = self.parse_command(message)

        if self.should_handle_message(opts, message):
            self.handle_message(opts, message)
