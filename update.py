#!/usr/bin/python3

import json
from xml.dom import minidom
import os
import jinja2 # Debian: python3-jinja2

BOOL = {
    'true':  True,
    'false': False,
}

def filter_active(highlightpath, currentpath):
    if highlightpath == currentpath:
        return 'active'

def render(out, template_name, **kwargs):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True)
    env.filters['active'] = filter_active
    template = env.get_template(template_name)
    html = template.render(base='.', assets='..', **kwargs)
    open(out, 'w').write(html)


def getText(element):
    strings = []
    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE:
            strings.append(node.data)
    return ''.join(strings)

def translated(element):
    strings = {}
    for child in element.childNodes:
        if child.nodeType != child.ELEMENT_NODE:
            continue
        strings[child.nodeName] = getText(child)
    return strings

def readAttribute(xml, credential):
    attribute = {
        'id':          xml.getAttribute('id'),
        'name':        translated(xml.getElementsByTagName('Name')[0]),
        'description': translated(xml.getElementsByTagName('Description')[0]),
    }
    attribute['identifier'] = '%s.%s' % (credential['identifier'], attribute['id'])
    return attribute

def readCredential(path):
    xml = minidom.parse(path + '/description.xml')
    credential = {
        'schememgr':         getText(xml.getElementsByTagName('SchemeManager')[0]),
        'issuer':            getText(xml.getElementsByTagName('IssuerID')[0]),
        'id':                getText(xml.getElementsByTagName('CredentialID')[0]),
        'name':              translated(xml.getElementsByTagName('Name')[0]),
        'shortName':         translated(xml.getElementsByTagName('ShortName')[0]),
        'description':       translated(xml.getElementsByTagName('Description')[0]),
        'logo':              path + '/logo.png',
        'shouldBeSingleton': False, # default?
        'attributes':        [],
    }
    credential['identifier'] = '%s.%s.%s' % (credential['schememgr'], credential['issuer'], credential['id'])

    singletonElements = xml.getElementsByTagName('ShouldBeSingleton')
    if singletonElements:
        # Not all credential descriptions have a ShouldBeSingleton element.
        credential['shouldBeSingleton'] = BOOL[getText(singletonElements[0])],

    for attribute in xml.getElementsByTagName('Attributes')[0].childNodes:
        if attribute.nodeType != attribute.ELEMENT_NODE:
            continue
        credential['attributes'].append(readAttribute(attribute, credential))

    return credential

def readIssuer(path):
    xml = minidom.parse(path + '/description.xml')
    issuer = {
        'id':           getText(xml.getElementsByTagName('ID')[0]),
        'schememgr':    getText(xml.getElementsByTagName('SchemeManager')[0]),
        'shortName':    translated(xml.getElementsByTagName('ShortName')[0]),
        'name':         translated(xml.getElementsByTagName('Name')[0]),
        'contactEmail': getText(xml.getElementsByTagName('ContactEMail')[0]),
        'logo':         path + '/logo.png',
        'credentials':  {},
    }
    issuer['identifier'] = '%s.%s' % (issuer['schememgr'], issuer['id'])

    for fn in sorted(os.listdir(path + '/Issues')):
        issuer['credentials'][fn] = readCredential(path + '/Issues/' + fn)

    return issuer

def readSchemeManager(path):
    index = {}

    xml = minidom.parse(path + '/description.xml')
    index = {
        'id':          getText(xml.getElementsByTagName('Id')[0]),
        'name':        translated(xml.getElementsByTagName('Name')[0]),
        'description': translated(xml.getElementsByTagName('Description')[0]),
        'url':         getText(xml.getElementsByTagName('Url')[0]),
        'contact':     getText(xml.getElementsByTagName('Contact')[0]),
        'issuers':     {},
    }

    for fn in sorted(os.listdir(path)):
        issuerPath = path + '/' + fn
        if os.path.exists(issuerPath + '/description.xml'):
            index['issuers'][fn] = readIssuer(issuerPath)

    return index


def generateHTML(index, out, lang):
    os.makedirs(out, exist_ok=True)
    render(out + '/index.html', 'about.html',
           index=index,
           LANG=lang,
           identifier='')

    for schememgr in index:
        for issuerId, issuer in sorted(schememgr['issuers'].items()):
            render(out + '/' + issuer['identifier'] + '.html', 'issuer.html',
                   index=index,
                   schememgr=schememgr,
                   issuer=issuer,
                   LANG=lang,
                   identifier=issuer['identifier'])
            for credentialId, credential in sorted(issuer['credentials'].items()):
                render(out + '/' + credential['identifier'] + '.html', 'credential.html',
                       index=index,
                       schememgr=schememgr,
                       issuer=issuer,
                       credential=credential,
                       LANG=lang,
                       identifier=credential['identifier'])


if __name__ == '__main__':
    schememanagers = ['pbdf-schememanager', 'irma-demo-schememanager']
    index = []
    for path in schememanagers:
        index.append(readSchemeManager(path))
    json.dump(index, open('index.json', 'w'))
    generateHTML(index, 'en', 'en')
