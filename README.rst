===============================
Ferrymang
===============================

.. image:: https://badge.fury.io/py/ferrymang.png
    :target: http://badge.fury.io/py/ferrymang

.. image:: https://travis-ci.org/wernesgruner/ferrymang.png?branch=master
        :target: https://travis-ci.org/wernesgruner/ferrymang

.. image:: https://pypip.in/d/ferrymang/badge.png
        :target: https://pypi.python.org/pypi/ferrymang


A git deployment tool.

* Free software: BSD license
* Documentation: https://ferrymang.readthedocs.org.

Installation
------------

Requirements:

* python3.x
* libssh2: http://www.libssh2.org/
* pygit2: http://www.pygit2.org/install.html

Usage
-----
usage: ferrymang.py [-h] --signature SIGNATURE --pubkpath PUBKPATH --prvkpath PRVKPATH --pkpasswd PKPASSWD [--giturl GITURL]

* signature : The github token as configured in your repository settings pages
* pubkpath : The path to your public ssh key
* prvkpath : The path to your private ssh key
* pkpasswd : The password to decrypt your ssh key
* giturl : The url of the repository which will be used to download your ferrymang.json configuration file if the cached version is unavailable for any reason.

Features
--------

* TODO