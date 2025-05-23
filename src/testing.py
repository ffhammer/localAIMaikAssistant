import json

from .accounts.accounts_loading import AccountSettings
from .models.message import MailMessage

TEST_ACCOUNT = AccountSettings(
    name="test",
    password="",
    imap_server="",
    user="test user",
    apple_mail_name="test",
    imap_inbox_folder="INBOX",
    imap_sent_folder="sent",
    apple_mail_inbox_folder="nothing",
    apple_mail_sent_folder="nothing",
    user_for_mail="Gustav the test User",
    input_port=999,
)


def load_test_messages(path) -> dict[str, MailMessage]:
    with open(path, "r") as f:
        data: list[dict] = json.loads(f.read())

    mails = [MailMessage.model_validate(mail) for mail in data]
    unique_mailboxes = {mail.mailbox for mail in mails}

    return {
        mailbox: [mail for mail in mails if mail.mailbox == mailbox]
        for mailbox in unique_mailboxes
    }
