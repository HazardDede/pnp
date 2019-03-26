"""Shared functionality for e-mail traffic."""

import mimetypes
import os
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..validator import Validator


class Mail:
    """Utility class for e-mail creation.
    Makes mime-compatible e-mails with or without attachments."""

    @staticmethod
    def _content_type(file_path):
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        return main_type, sub_type

    @staticmethod
    def _file_contents(file_path, file_type):
        with open(file_path, 'r' if file_type == 'text' else 'rb') as fp:
            return fp.read()

    @staticmethod
    def _make_attachment(file_path, contents, main_type, sub_type):
        if main_type == 'text':
            msg = MIMEText(contents, _subtype=sub_type)
        elif main_type == 'image':
            from email.mime.image import MIMEImage
            msg = MIMEImage(contents, _subtype=sub_type)
        elif main_type == 'audio':
            from email.mime.audio import MIMEAudio
            msg = MIMEAudio(contents, _subtype=sub_type)
        else:
            from email.mime.base import MIMEBase
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(contents)

        encoders.encode_base64(msg)
        filename = os.path.basename(file_path)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        return msg

    @classmethod
    def create_with_attachment(cls, sender, recipient, subject, file_path, message_text=None):
        """Create a message for an email.

        Example:

            >>> import tempfile
            >>> with tempfile.NamedTemporaryFile() as attach:
            ...     res = Mail.create_with_attachment('sender', 'a@a.com', 'subject',
            ...                                        attach.name, 'Message text')
            >>> res['to'], res['from'], res['subject']
            ('a@a.com', 'sender', 'subject')

        Args:
            sender: Email address of the sender.
            recipient: Email address of the receiver.
            subject: The subject of the email message.
            message_text: The text of the email message.
            file_path: The path to the file to be attached.

        Returns:
            An object containing a base64url encoded email object.
        """
        Validator.is_file(file_path=file_path)

        message = MIMEMultipart()
        message['to'] = str(recipient)
        message['from'] = str(sender)
        message['subject'] = str(subject)
        if message_text is not None:
            msg = MIMEText(str(message_text))
            message.attach(msg)

        main_type, sub_type = cls._content_type(file_path)
        file_contents = cls._file_contents(file_path, main_type)
        attachment = cls._make_attachment(file_path, file_contents, main_type, sub_type)
        message.attach(attachment)

        return message

    @classmethod
    def create_text(cls, sender, recipient, subject, message_text):
        """Create a message for an email.

        Example:

        Example:

            >>> res = Mail.create_text('sender', 'a@a.com', 'subject', 'Message text')
            >>> res['to'], res['from'], res['subject']
            ('a@a.com', 'sender', 'subject')

        Args:
            sender: Email address of the sender.
            recipient: Email address of the receiver.
            subject: The subject of the email message.
            message_text: The text of the email message.

        Returns:
            An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = str(recipient)
        message['from'] = str(sender)
        message['subject'] = str(subject)

        return message
