"""
The search() method in imaplib accepts IMAP search criteria,
so you can filter by sender, subject, date, flags, text,
and more instead of using "ALL".

Gmail-specific searches:
  Gmail supports its own powerful search syntax via the special
  X-GM-RAW extension. This lets you use the same queries you
  type into the Gmail search bar.

INFO:
  1. Simple Syntax:
    (status, messages) = imap.search(None, <criteria>)
  2. Combining Filters Using Parenthesis:
    '(
      FROM "<email>" SINCE "<day>-<month>-<year>" UNSEEN
    )'

NOTE:
  1. <day> < 10 should start with 0 & <month> is 3-letter abbrv
"""

from enum import StrEnum, unique
# from frozendict import frozendict
# from pprint import pprint as print

# Custom frozendict wrapper
# class FrozenObject(frozendict):
#   def __getattr__(self, key: str) -> str:
#     return self[key]


# Gmail folders
@unique
class GmailFolders(StrEnum):
  INBOX = "INBOX"  # Incoming mail
  ALL = "[Gmail]/All Mail"  # Everything except Spam/Trash
  DRAFTS = "[Gmail]/Drafts"  # Unsent drafts
  SENT = "[Gmail]/Sent Mail"  # Sent messages
  SPAM = "[Gmail]/Spam"  # Spam
  TRASH = "[Gmail]/Trash"  # Deleted messages
  STARRED = "[Gmail]/Starred"  # Starred messaegs
  IMPORTANT = "[Gmail]/Important"  # Gmail's Important marker
  SNOOZED = "[Gmail]/Snoozed"  # Snoozed messages


# Gmail filters
@unique
class GmailFilters(StrEnum):
  ALL = "ALL"
  UNREAD = "UNSEEN"
  UNREAD_EMAILS_FROM_SENDER = '(UNSEEN FROM "<email>")'
  UNREAD_EMAILS_WITH_SUBJECT = '(UNSEEN SUBJECT "<subject>")'
  READ = "SEEN"
  FROM_SENDER = 'FROM "<email>"'
  TO_RECIPIENT = 'TO "<email>"'
  SUBJECT_CONTAINS = 'SUBJECT "<subject>"'
  BODY_CONTAINS = 'BODY "<body>"'
  TEXT_ANYWHERE = 'TEXT "<text>"'
  SINCE_DATE = 'SINCE "<day>-<month>-<year>"'
  BEFORE_DATE = 'BEFORE "<day>-<month>-<year>"'
  ON_SPECIFIC_DATE = 'ON "<day>-<month>-<year>"'
  HAS_ATTACHMENTS = 'HEADER Content-Type "multipart/mixed"'
  FLAGGED = "FLAGGED"
  ANSWERED = "ANSWERED"
  DELETED = "DELETED"
  DRAFTS = "DRAFT"
  X_GM_RAW = 'X-GM-RAW "<query>"'
