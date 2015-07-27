# tindicator
Toggl indicator for Unity (Ubuntu)

This is a simple indicator for Ubuntu desktop, which is built in order to improve
the visibility of [Toggl time tracker](https://toggl.com/) on Ubuntu.

![ScreenShot](http://dl.dropbox.com/u/15708031/Selection_324.png)

You can create a .deb file from the package using [stdeb](https://pypi.python.org/pypi/stdeb)

```
python setup.py --command-packages=stdeb.command bdist_deb

```