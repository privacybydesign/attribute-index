# Attribute index

Generate documentation for the IRMA scheme manager. You can browse a live
version [over here](https://privacybydesign.foundation/attribute-index/en/).

## Installing

Dependencies:

  * git (to clone the scheme managers)
  * Python 3
  * [Jinja2](http://jinja.pocoo.org/) (Debian package: `python3-jinja2`)
  * yarn

Before content can be generated, the scheme managers need to be downloaded:

```bash
git clone https://github.com/privacybydesign/pbdf-schememanager.git
git clone https://github.com/privacybydesign/irma-demo-schememanager.git
```

Currently the paths for these are hardcoded, but that can be changed if needed.

## Running

To generate the HTML for the attribute index, run the script:

```bash
python3 update.py
```

If you want to have an up-to-date attribute index, it is recommended to update
the scheme managers regularly and run the update script afterwards.

To generate the JavaScript handling issuance sessions of demo credentials, run:

```bash
npm i
npm run build
```

## Using untrusted scheme managers

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
