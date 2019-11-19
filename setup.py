from setuptools import setup, find_packages


VERSION = '0.20.2'


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='pnp',
    version=VERSION,
    description="Pull 'n' Push",
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/HazardDede/pnp',
    author='d.muth',
    author_email='nicetry@bitch.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Home Automation',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='push pull data pipeline',
    project_urls={
        'Documentation': 'https://github.com/HazardDede/pnp/blob/master/index.md',
        'Source': 'https://github.com/HazardDede/pnp/',
        'Tracker': 'https://github.com/HazardDede/pnp/issues',
    },
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'argresolver>=0.3.2',
        'asyncio>=3.4.0',
        'asyncws>=0.1',
        'attrs>=18.0.0',
        'binaryornot>=0.4.4',
        'cronex>=0.1.3',
        'dictmentor>=0.2.0',
        'docopt>=0.6.2',
        'glom>=19.2.0',
        'Jinja2>=2.0',
        'psutil>=5.4.8',
        'python-box>=3.2.0',
        'pytz>=2018.4',
        'influxdb>=5.0.0',
        'paho-mqtt>=1.3.1',
        'requests>=2.18.4',
        'ruamel.yaml>=0.15.37',
        'schedule>=0.5.0',
        'schema>=0.6.7',
        'schiene>=0.23',
        'slacker>=0.9.0',
        'syncasync>=20180812',
        'typing-extensions>=3.7.2',
        'tzlocal>=1.5.0'
    ],
    extras_require={
        'dht': ['Adafruit_DHT>=1.3.2'],
        'dropbox': ['dropbox>=9.0.0', 'urllib3<1.25,>=1.20'],
        'faceR': ['image>=1.5.24', 'face-recognition>=1.2.2'],
        'fitbit': ['fitbit>=0.3.0'],
        'fswatcher': ['watchdog>=0.8.3'],
        'ftp': ['pyftpdlib>=1.5.0'],
        'gmail': ['google-api-python-client>=1.7.7', 'google-auth-httplib2>=0.0.3', 'google-auth-oauthlib>=0.2.0'],
        'gpio': ['RPi.GPIO>=0.6.5'],
        'http-server': ['Flask>=1.0.2', 'gevent>=1.3.4', 'sanic<=18.12.0'],
        'miflora': ['miflora>=0.4.0'],
        'pushbullet': ['pushbullet.py>=0.10.0', 'urllib3<1.25,>=1.20'],
        'sound': ['PyAudio>=0.2.11', 'scipy>=1.2.0']
    },
    python_requires='>=3.5',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pnp=pnp.runner.pnp:main',
            'pnp_gmail_tokens=pnp.runner.pnp_gmail_tokens:main',
            'pnp_record_sound=pnp.runner.pnp_record_sound:main'
        ],
    },
)
