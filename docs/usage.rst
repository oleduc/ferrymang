========
Usage
========

usage: ferrymang.py [-h] --pubkpath PUBKPATH --prvkpath PRVKPATH --pkpasswd PKPASSWD --signature SIGNATURE [--giturl GITURL] [--ip IP] [--port PORT]

* signature : The github token as configured in your repository settings pages
* pubkpath : The path to your public ssh key
* prvkpath : The path to your private ssh key
* pkpasswd : The password to decrypt your ssh key
* giturl : The url of the repository which will be used to download your ferrymang.json configuration file if the cached version is unavailable for any reason.