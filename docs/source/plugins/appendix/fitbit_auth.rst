Fitbit Authentication
^^^^^^^^^^^^^^^^^^^^^

To request data from the fitbit account it is necessary to create an app. Go to `dev.fitbit.com <https://dev.fitbit.com/>`_.
Under ``Manage`` go to ``Register an App``.

For the application website and organization website, name it anything starting with ``http://`` or ``https://``.
Secondly, make sure the OAuth 2.0 Application Type is ``Personal``.
Lastly, make sure the Callback URL is ``http://127.0.0.1:8080/`` in order to get our Fitbit API to connect properly.
After that, click on the agreement box and submit. You will be redirected to a page that contains your ``Client ID`` and
your ``Client Secret``.

Next we need to acquire your initial ``access``- and ``refresh``-token.

.. code-block:: shell

   git clone https://github.com/orcasgit/python-fitbit.git
   cd python-fitbit
   python3 -m venv venv
   source venv/bin/activate
   pip install -r dev.txt
   ./gather_keys_oauth2.py <client_id> <client_secret>


You will be redirected to your browser and asked to login to your fitbit account. Next you can restrict the app to
certain data. If everything is fine, your console window should print your ``access``- and ``refresh``-token and also
``expires_at``.

Put your ``client_id``, ``client_secret``, ``access_token``, ``refresh_token`` and ``expires_at`` to a yaml file and use this
file-path as the ``config`` argument of this plugin. Please see the example below:

.. code-block:: yaml

   access_token: <access_token>
   client_id: <client_id>
   client_secret: <client_secret>
   expires_at: <expires_at>
   refresh_token: <refresh_token>

That's it. If your token expires it will be refreshed automatically by the plugin.
