from setuptools import setup, find_packages

setup(
    name='tindicator',
    version='1.0.1',
    include_package_data=True,
    entry_points = {
        'console_scripts' : ['tindicator = toggl.toggle_indicator:main']
    },
    data_files = [
        ('share/applications/', ['tindicator.desktop']),
        ('share/toggle_indicator/toggl', ['toggl/toggl_ui.glade', 'toggl/toggl.png'])
    ],
    packages=['toggl'],
)

