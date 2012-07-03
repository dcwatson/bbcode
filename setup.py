from distutils.core import setup
import bbcode

setup(
    name='bbcode',
    version=bbcode.__version__,
    description='A pure python bbcode parser and formatter.',
    author='Dan Watson',
    author_email='dcwatson@gmail.com',
    url='https://github.com/dcwatson/bbcode',
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
