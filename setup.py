from distutils.core import setup
import sys

setup(
    name='bbcode',
    version='1.0.5',
    description='A pure python bbcode parser and formatter.',
    author='Dan Watson',
    author_email='dcwatson@gmail.com',
    url='https://bitbucket.org/dcwatson/bbcode',
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
