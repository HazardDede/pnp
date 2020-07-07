GMail Token Generation
^^^^^^^^^^^^^^^^^^^^^^

Goto `https://console.developers.google.com <https://console.developers.google.com>`` and create a new project.

Goto ``Dashboard`` and click ``Enable API's and Services``. Search ``gmail`` and enable the api.

Goto ``Credentials``, then ``OAuth consent screen`` and set the ``Application Name``. Save the form.

Goto ``Credentials`` and select ``Create credentials`` and ``OAuth client id``.
Select ``Other`` and name it as you see fit.

Afterwards download your credentials as a json file.

Run ``pnp_gmail_tokens <credentials.json> <out_tokens.pickle>``.

You will be requested to login to your GMail account and accept the requested scopes (sending mails on your behalf).
If this went well, the tokens for your previously downloaded credentials will be created.
The ``<out_tokens.pickle>`` is the file you have to pass as the ``token_file`` to this component.