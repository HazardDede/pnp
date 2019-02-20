import os
from tempfile import NamedTemporaryFile

import mock
import pytest

from pnp.plugins.push.mail import GMail


class CredentialDummy:
    def __init__(self, valid=True, expired=False):
        self._valid = valid
        self._expired = expired

    @property
    def valid(self):
        return self._valid

    @property
    def expired(self):
        return self._expired

    @property
    def refresh_token(self):
        return 'refresh_token'

    def refresh(self, transport):
        self._valid = True
        self._expired = False


@pytest.fixture(scope='function')
def token_file():
    import pickle
    with NamedTemporaryFile('wb', delete=False) as fp:
        pickle.dump(CredentialDummy(), fp)

    yield fp.name
    if os.path.isfile(fp.name):
        os.remove(fp.name)


@pytest.fixture(scope='function')
def expired_token_file():
    import pickle
    with NamedTemporaryFile('wb', delete=False) as fp:
        pickle.dump(CredentialDummy(valid=False, expired=True), fp)

    yield fp.name
    if os.path.isfile(fp.name):
        os.remove(fp.name)


@pytest.fixture(scope='function')
def attachment():
    with NamedTemporaryFile('wb') as fp:
        yield fp.name


@mock.patch('googleapiclient.discovery.build')
@mock.patch('google.auth.transport.requests.Request')
@mock.patch('pnp.plugins.push.mail.Mail.create_text')
def test_gmail_for_smoke(mail_create_text, google_request, google_build, token_file):
    mail_create_text.return_value = mock.Mock(as_bytes=lambda: b'12345678')

    dut = GMail(name='pytest', token_file=token_file, recipient='anybody@somebody.com', subject='subject')
    dut.push("This is the content")

    mail_create_text.assert_called_with('pnp', 'anybody@somebody.com', 'subject', 'This is the content')

    google_build.assert_called_once()
    google_build.return_value.users.assert_called_once()
    google_build.return_value.users.return_value.messages.assert_called_once()
    google_build.return_value.users.return_value.messages.return_value.send.assert_called_once()
    google_build.return_value.users.return_value.messages.return_value.send.return_value.execute.assert_called_once()


@mock.patch('googleapiclient.discovery.build')
@mock.patch('google.auth.transport.requests.Request')
@mock.patch('pnp.plugins.push.mail.Mail.create_with_attachment')
def test_gmail_with_attachment_for_smoke(mail_create_attach, google_request, google_build, token_file, attachment):
    mail_create_attach.return_value = mock.Mock(as_bytes=lambda: b'12345678')

    dut = GMail(name='pytest', token_file=token_file, recipient='anybody@somebody.com', subject='subject')
    dut.push(dict(data="This is the content", attachment=attachment))

    mail_create_attach.assert_called_with('pnp', 'anybody@somebody.com', 'subject', attachment,'This is the content')

    google_build.assert_called_once()
    google_build.return_value.users.assert_called_once()
    google_build.return_value.users.return_value.messages.assert_called_once()
    google_build.return_value.users.return_value.messages.return_value.send.assert_called_once()
    google_build.return_value.users.return_value.messages.return_value.send.return_value.execute.assert_called_once()


@mock.patch('googleapiclient.discovery.build')
@mock.patch('google.auth.transport.requests.Request')
def test_gmail_for_token_refresh(google_request, google_build, expired_token_file):
    dut = GMail(name='pytest', token_file=expired_token_file, recipient='anybody@somebody.com', subject='subject')
    dut.push("This is the content")

    google_build.assert_called_once()
    google_request.assert_called_once()

    import pickle
    with open(expired_token_file, 'rb') as fp:
        creds = pickle.load(fp)
        assert creds.valid
        assert not creds.expired


@mock.patch('googleapiclient.discovery.build')
@mock.patch('google.auth.transport.requests.Request')
@mock.patch('pnp.plugins.push.mail.Mail.create_text')
def test_gmail_envelope_override(mail_create_text, google_request, google_build, token_file):
    mail_create_text.return_value = mock.Mock(as_bytes=lambda: b'12345678')

    dut = GMail(name='pytest', token_file=token_file, recipient='anybody@somebody.com', subject='subject')
    dut.push(dict(subject='new subject', recipient='a@a.com', data='This is the content', sender='sender'))

    mail_create_text.assert_called_with('sender', 'a@a.com', 'new subject', 'This is the content')


@mock.patch('googleapiclient.discovery.build')
@mock.patch('google.auth.transport.requests.Request')
@mock.patch('pnp.plugins.push.mail.Mail.create_text')
def test_gmail_multiple_recipients(mail_create_text, google_request, google_build, token_file):
    mail_create_text.return_value = mock.Mock(as_bytes=lambda: b'12345678')

    dut = GMail(name='pytest', token_file=token_file, recipient=['a@a.com', 'b@b.com'], subject='subject')
    dut.push("This is the content")

    mail_create_text.assert_called_with('pnp', 'a@a.com,b@b.com', 'subject', 'This is the content')
