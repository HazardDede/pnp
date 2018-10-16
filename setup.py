from setuptools import setup, find_packages


VERSION = '0.11.1'


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
        'Documentation': 'https://github.com/HazardDede/pnp/blob/master/README.md',
        'Source': 'https://github.com/HazardDede/pnp/',
        'Tracker': 'https://github.com/HazardDede/pnp/issues',
    },
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        'argresolver>=0.3.1',
        'binaryornot>=0.4.4',
        'dictmentor>=0.1.0',
        'docopt>=0.6.2',
        'Flask>=1.0.2',
        'gevent>=1.3.4',
        'python-box>=3.2.0',
        'pytz>=2018.4',
        'influxdb>=5.0.0',
        'paho-mqtt>=1.3.1',
        'requests>=2.18.4',
        'ruamel.yaml>=0.15.37',
        'schedule>=0.5.0',
        'schema>=0.6.7',
        'tzlocal>=1.5.0'
    ],
    extras_require={
        'dht': ['Adafruit_DHT==1.3.2'],
        'fswatcher': ['watchdog>=0.8.3'],
        'faceR': ['image>=1.5.24', 'face-recognition>=1.2.2']
    },
    dependency_links=[
        "git+https://github.com/adafruit/Adafruit_Python_DHT.git#egg=Adafruit_DHT-1.3.2"
    ],
    python_requires='>=3.5',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pnp=pnp.runner.pnp:main',
        ],
    },
)
