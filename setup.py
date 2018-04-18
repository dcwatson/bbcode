import bbcode
from setuptools import setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='bbcode',
    version=bbcode.__version__,
    description='A pure python bbcode parser and formatter.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dan Watson',
    author_email='dcwatson@gmail.com',
    url='https://github.com/dcwatson/bbcode',
    project_urls={
        'Documentation': 'http://bbcode.readthedocs.io/',
    },
    license='BSD',
    py_modules=['bbcode'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3",
        'Topic :: Text Processing :: Markup',
    ]
)
