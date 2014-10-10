=============
Configuration
=============

Supported variables:

* {branch} : Branch name
* {path} : Path of the current application
* {random} : A random variable [*]

Example:

.. code:: javascript

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
              "type": "delete",
              "path": "./some-folder-relative-to-configured-root/config/"
          },
          {
              "type": "mkdir",
              "path": "./some-folder-relative-to-configured-root/config/"
          },
          {
              "type": "move",
              "from": "./home/config/example",
              "to"  : "./app-two/config.json"
          }
      ]
    }
