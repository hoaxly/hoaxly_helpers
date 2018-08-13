import os
from setuptools import setup

# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    """ Utility function to read the README file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="hoaxlyHelpers",
    version="1.2.4",
    description=("python helpers for hoaxly"),
    license="BSD",
    packages=['hoaxlyHelpers'],

)
