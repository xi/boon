#!/usr/bin/env python

from setuptools import setup

README = open('README.md').read()


setup(
    name='boon',
    version='0.0.0',
    description='unix terminal framework',
    long_description=README,
    url='https://github.com/xi/boon',
    author='Tobias Bengfort',
    author_email='tobias.bengfort@posteo.de',
    py_modules=['boon'],
    license='MIT',
    classifiers=[
        'Environment :: Console :: Curses',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: User Interfaces',
    ],
)
