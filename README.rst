===============================
Ferrymang
===============================

A simple github deployment tool.

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


Configuration
_____________

Supported variables:

* {branch} : Branch name
* {path} : Path of the current application
* {random} : A random variable [*]

Example:

.. code:: json
    {
      "root": "/var/applications/",
      "applications": {
          "app-one": {
              "path": "./app-one-{branch}/",
              "main": true,
              "start": {
                  "commands": [
                      "npm install",
                      "forever start --uid \"api-{branch}\" {path}/app.js"
                  ],
              },
              "stop": {
                  "path": "./stop.sh",
                  "parameters": "{branch}"
              }
          },
          "app-two":{
              "path": "./app-two-server/",
              "main": false,
              "start": {
                  "path": "./start.sh",
                  "parameters": "{branch} arg2 {path} etc"
              },
              "stop": {
                  "command": "forever stop --uid app-two {path}/app.js",
                  "parameters": "{branch}"
              }
          }
      },
      "actions" : [
          {
              "type": "move",
              "from": "./some-cloned-folder-relative-to-repo-root/config/*",
              "to"  : "./some-folder-relative-to-configured-root/config/"
          },
          {
              "type": "move",
              "from": "./home/config/example",
              "to"  : "./app-two/config.json"
          }
      ]
    }


Features
--------

* Listen to github push events
* Clone one or multiple git repositories
* Parse a list of actions (JSON) and execute it
* Execute start/stop scripts

Todo
____

* Database deployment
* Multiple repositories