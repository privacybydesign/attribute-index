# Attribute index

Generate documentation for the Yivi scheme manager. You can browse a live
version [over here](https://privacybydesign.foundation/attribute-index/en/).

## Installing

Dependencies:

  * git (to clone the scheme managers)
  * Python 3
  * [Jinja2](http://jinja.pocoo.org/) (Debian package: `python3-jinja2`)
  * yarn


## Running

Before you run the script to generate Yivi index pages run the `download_repos.py` script. This downloalds
most recent version of the schemes. If new schemes are added, you can modify the `config.json` file to add them.

    python3 download_repos.py
    python3 generate-index.py


To generate the JavaScript handling issuance sessions of demo credentials, run:

    yarn
    yarn run build

## Running with Docker

To build and run the Docker container, you can use docker compose:

    docker compose up

Currently, scheme managers are considered trusted. Generating an attribute index
for an untrusted scheme manager has at least the following problems at the
moment:

  * URLs are not validated yet. They could start with `javascript:`, leading to
    [XSS](https://www.owasp.org/index.php/Cross-site_Scripting_(XSS)).
  * XML parsers are by default often vulnerable to security problems like the
    "billion laughs" attack, which causes enormous amounts of RAM to be used by
    the script. This is likely the case for the update script as well.

So, before an attribute index can be generated from untrusted scheme managers,
these problems (and possibly others) need to be fixed first.
