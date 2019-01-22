import base64
import os

from . import PushBase
from .. import load_optional_module
from ...shared.mime import Mail
from ...utils import FileLock, make_list, is_iterable_but_no_str
from ...validator import Validator


class GMail(PushBase):
    __prefix__ = 'gmail'
    EXTRA = 'gmail'

    def __init__(self, token_file, recipient, subject=None, sender='pnp', **kwargs):
        super().__init__(**kwargs)
        self.token_file = str(token_file)
        if not os.path.isabs(self.token_file):
            self.token_file = os.path.join(self.base_path, self.token_file)
        Validator.is_file(token_file=self.token_file)

        self.recipient = self._parse_recipient(recipient)
        self.subject = self._parse_subject(subject)
        self.sender = self._parse_sender(sender)

    @staticmethod
    def _create_message(sender, to, subject, message_text=None, attachment=None):
        if is_iterable_but_no_str(to):
            to = ",".join(to)
        if attachment is None:
            mail = Mail.create_text(sender, to, subject, message_text)
        else:
            mail = Mail.create_with_attachment(sender, to, subject, attachment, message_text)
        return {'raw': base64.urlsafe_b64encode(mail.as_bytes()).decode()}

    def _parse_recipient(self, val):
        to = make_list(val)
        return [str(v) for v in to]

    def _parse_subject(self, val):
        return val and str(val)

    def _parse_sender(self, val):
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

            # Check if the given credentials are still valid... If no: Might be outdated so refresh them
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
        except:
            import traceback
            error = traceback.format_exc()
            self.logger.error("[{self.name}] Error: {error}".format(**locals()))

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)
        recipient = self._parse_envelope_value('recipient', envelope)  # Override recipient via envelope
        subject = self._parse_envelope_value('subject', envelope)  # Override subject via envelope
        sender = self._parse_envelope_value('sender', envelope)  # Override sender via envelope
        file_path = envelope.get('attachment')

        if subject is None:
            raise ValueError("Subject was not defined either by the __init__ nor by the envelope")
        Validator.is_file(allow_none=True, file_path=file_path)

        self.logger.info("[{self.name}] Sending E-Mail '{subject}' to {recipient}\n"
                         "Content: '{real_payload}' (Attachment: '{file_path}')".format(**locals()))

        message = self._create_message(sender, recipient, subject, real_payload, file_path)
        service = self._make_service(self.token_file)
        self._send_message(service, message)

        return payload
