"""Pull 'n' Push GMail Token Creator"""

import pickle

import click
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the token file
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


@click.command('pnp_gmail_tokens')
@click.argument(
    'credential_file',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True,
)
@click.argument(
    'token_file',
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    required=True,
)
def main(credential_file, token_file):
    """Pull 'n' Push GMail Token Creator."""
    flow = InstalledAppFlow.from_client_secrets_file(credential_file, SCOPES)
    creds = flow.run_local_server()

    with open(token_file, 'wb') as tfp:
        pickle.dump(creds, tfp)

    print("Tokens successfully written to: {}".format(token_file))


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
