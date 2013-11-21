import os
from setuptools import setup

VERSION = "0.0.1"

# Utility function to read the README file.
# Used for the long_description.
# It's nice, because:
#   1) we have a top level README file
#   2) it's easier to type in the README file than to put a raw string

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "bottle-memcache-decorator",
    packages = ['bottle_memcache_decorator'],
    package_data = {
        'bottle-memcache-decorator': ['LICENSE', 'README.md']
    },
	version = VERSION,
	author = "Chris Ziogas",
	author_email = "ziogas_chr@hotmail.com",
    url = "http://github.com/ziogaschr/bottle-memcache-decorator",
    download_url='https://github.com/ziogaschr/bottle-memcache-decorator/tarball/v%s#egg=ziogaschr/bottle-memcache-decorator-%s' % (VERSION, VERSION),
    description = ("Adds a memcache decorator in your Bottle application. \
        It automatically stores the route result to memcache for routes \
        where the bottle-memcache plugin is enabled."),
    license = "MIT",
    platforms = 'any',
    keywords = "Bottle Plugin Memcache Decorator",
	long_description = read('README.md'),
	classifiers = [
		"Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Framework :: Bottle",
		"License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
	],
    install_requires = [
        'bottle>=0.11',
        'bottle-extras',
        'bottle_memcache'
    ],
    test_suite = 'bottle_memcache_decorator/tests'
)
