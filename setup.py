from setuptools import setup, find_packages

setup(
    name='toggl-indicator',
    version='1.0',
    entry_points = {
        'console_scripts' : ['myscript = toggl.toggl_indicator:main']
    },
    packages=find_packages()
)

