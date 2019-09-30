from setuptools import setup, find_packages

NAME = "owntracker"
DESCRIPTION = "Personal location tracking system - own your location data"
URL = "https://github.com/lalanza808/owntracker"
EMAIL = "lance@lzahq.tech"
AUTHOR = "Lance Allen"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "0.0.1"
REQUIRED = [
    "pyramid",
    "zappa",
    "boto3",
    "pytz"
]
EXTRAS = {}
TESTS = []
SETUP = []

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    include_package_data=True,
    extras_require=EXTRAS,
    install_requires=REQUIRED,
    setup_requires=SETUP,
    tests_require=TESTS,
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'init_zappa=owntracker.init:init_zappa',
            'init_config=owntracker.init:init_config'
        ]
    }
)
