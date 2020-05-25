"""Pull 'n' Push GMail Token Creator

Usage:
  pnp_gmail <credential_file> <token_file>
  pnp_gmail (-h | --help)

Options:
  -h --help         Show this screen.

Args:
  credential_file   Obtained from GMail
  token_file        Output tokens (existing file will be overwritten)

"""

import os
import pickle

from docopt import docopt
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the token file
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def run(credential_file, token_file):
    """Run the utility script pnp_gmail_tokens."""
    if not os.path.isfile(credential_file):
        print("Credential file '{}' does not exist".format(credential_file))
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(credential_file, SCOPES)
    creds = flow.run_local_server()

    with open(token_file, 'wb') as tfp:
        pickle.dump(creds, tfp)

    print("Tokens successfully written to: {}".format(token_file))
    return 0


def main():
    """Main entry point for utility script pnp_gmail_tokens."""
    arguments = docopt(__doc__)
    creds, token = arguments['<credential_file>'], arguments['<token_file>']
    return run(creds, token)


if __name__ == '__main__':
    import sys
    sys.exit(main())
