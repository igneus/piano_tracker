from setuptools import setup

setup(
    name='piano_tracker',
    version='0.1',
    description='Tracks your exercising efforts on a MIDI-connected piano, produces stats',
    url='http://github.com/igneus/piano-tracker',
    author='Jakub Pavlík',
    author_email='jkb.pavlik@gmail.com',
    license='GPL 3.0',
    packages=['piano_tracker'],
    entry_points = {
        'console_scripts': ['piano_tracker=piano_tracker.app:main'],
    },
    zip_safe=False
)
