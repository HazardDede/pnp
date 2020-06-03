"""E-mail related push plugins."""

import base64
import os

from pnp import validator
from pnp.plugins import load_optional_module
from pnp.plugins.push import PushBase, enveloped, parse_envelope
from pnp.shared.mime import Mail
from pnp.utils import FileLock, make_list, is_iterable_but_no_str


class GMail(PushBase):
    """
    Sends an e-mail via the gmail api.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/mail.GMail/index.md
    """
    EXTRA = 'gmail'

    def __init__(self, token_file, recipient, subject=None, sender='pnp', **kwargs):
        super().__init__(**kwargs)
        self.token_file = str(token_file)
        if not os.path.isabs(self.token_file):
            self.token_file = os.path.join(self.base_path, self.token_file)
        validator.is_file(token_file=self.token_file)

        self.recipient = self._parse_recipient(recipient)
        self.subject = self._parse_subject(subject)
        self.sender = self._parse_sender(sender)

    @staticmethod
    def _create_message(sender, recipient, subject, message_text=None, attachment=None):
        if is_iterable_but_no_str(recipient):
            recipient = ",".join(recipient)
        if attachment is None:
            mail = Mail.create_text(sender, recipient, subject, message_text)
        else:
            mail = Mail.create_with_attachment(sender, recipient, subject, attachment, message_text)
        return {'raw': base64.urlsafe_b64encode(mail.as_bytes()).decode()}

    @staticmethod
    def _parse_recipient(val):
        recipients = make_list(val)
        return [str(v) for v in recipients]

    @staticmethod
    def _parse_subject(val):
        return val and str(val)

    @staticmethod
    def _parse_sender(val):
        return str(val)

    def _make_service(self, token_file):
        discovery = load_optional_module('googleapiclient.discovery', self.EXTRA)

        if not os.path.exists(token_file):
            raise RuntimeError("No credentials retrieved. Make sure '{}' exists".format(token_file))

        with FileLock(token_file):
            # The file token_file stores the user's access and refresh tokens
            import pickle
            with open(token_file, 'rb') as tokenfp:
                creds = pickle.load(tokenfp)

            # Check if the given credentials are still valid...
            # If no: Might be outdated so refresh them
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    requests = load_optional_module('google.auth.transport.requests', self.EXTRA)
                    creds.refresh(requests.Request())
                    # Save the credentials for the next run
                    import pickle
                    with open(token_file, 'wb') as tokenfp:
                        pickle.dump(creds, tokenfp)
                else:
                    raise RuntimeError("Tokens are not valid and cannot be refreshed! Period.")

        return discovery.build('gmail', 'v1', credentials=creds, cache_discovery=False)

    def _send_message(self, service, message, user_id='me'):
        """Send an email message.

        Args:
            service: Authorized Gmail API service instance.
            message: Message to be sent.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.

        Returns:
            Sent Message.
        """
        try:
            return service.users().messages().send(userId=user_id, body=message).execute()
        except:  # pylint: disable=bare-except
            self.logger.exception("Sending the e-mail via gmail failed")

    @enveloped
    @parse_envelope('recipient')
    @parse_envelope('subject')
    @parse_envelope('sender')
    def push(self, recipient, subject, sender, envelope, payload):  # pylint: disable=arguments-differ
        file_path = envelope.get('attachment')

        if subject is None:
            raise ValueError("Subject was not defined either by the __init__ nor by the envelope")
        if file_path:
            validator.is_file(file_path=file_path)

        self.logger.info(
            "Sending E-Mail '%s' to %s\n"
            "Content: '%s' (Attachment: '%s')",
            subject, recipient, payload, file_path
        )

        message = self._create_message(sender, recipient, subject, payload, file_path)
        service = self._make_service(self.token_file)
        self._send_message(service, message)

        return {'data': payload, **envelope} if envelope else payload
