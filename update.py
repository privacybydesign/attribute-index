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
    else:
        return ''

def render(out, template_name, **kwargs):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True)
    env.filters['active'] = filter_active
    template = env.get_template(template_name)
    html = template.render(base='.', assets='..', **kwargs)
    open(out, 'w', encoding='utf-8').write(html)


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
    name = xml.getElementsByTagName('Name')
    desc = xml.getElementsByTagName('Description')
    attribute = {
        'id':          xml.getAttribute('id'),
        'optional':    len(xml.getAttribute('optional')) > 0,
        'revocation':  len(xml.getAttribute('revocation')) > 0,
        'name':        translated(name[0]) if len(name) > 0 else None,
        'description': translated(desc[0]) if len(desc) > 0 else None,
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
        'revocation':        xml.getElementsByTagName('RevocationServers').length > 0,
        'logo':              path + '/logo.png',
        'shouldBeSingleton': False,
        'attributes':        [],
    }
    credential['identifier'] = '%s.%s.%s' % (credential['schememgr'], credential['issuer'], credential['id'])

    singletonElements = xml.getElementsByTagName('ShouldBeSingleton')
    if singletonElements:
        # Not all credential descriptions have a ShouldBeSingleton element.
        credential['shouldBeSingleton'] = BOOL[getText(singletonElements[0])]

    for attribute in xml.getElementsByTagName('Attributes')[0].childNodes:
        if attribute.nodeType != attribute.ELEMENT_NODE:
            continue
        credentialAttr = readAttribute(attribute, credential)
        if credentialAttr['revocation']:
            continue
        credential['attributes'].append(credentialAttr)

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

def readSchemeManager(path, githubURL):
    schememgr = {}

    xml = minidom.parse(path + '/description.xml')
    schememgr = {
        'id':                getText(xml.getElementsByTagName('Id')[0]),
        'name':              translated(xml.getElementsByTagName('Name')[0]),
        'description':       translated(xml.getElementsByTagName('Description')[0]),
        'url':               getText(xml.getElementsByTagName('Url')[0]),
        'github':            githubURL,
        'contact':           getText(xml.getElementsByTagName('Contact')[0]),
        'keyshareServer':    None,
        'keyshareWebsite':   None,
        'keyshareAttribute': None,
        'issuers':           {},
    }
    schememgr['identifier'] = schememgr['id'] # for consistency
    schememgr['test'] = bool(os.path.exists(path + '/sk.pem'))

    keyshareServerElements = xml.getElementsByTagName('KeyshareServer')
    if keyshareServerElements:
        schememgr['keyshareServer'] = getText(keyshareServerElements[0])

    keyshareWebsiteElements = xml.getElementsByTagName('KeyshareWebsite')
    if keyshareWebsiteElements:
        schememgr['keyshareWebsite'] = getText(keyshareWebsiteElements[0])

    keyshareAttributeElements = xml.getElementsByTagName('KeyshareAttribute')
    if keyshareAttributeElements:
        schememgr['keyshareAttribute'] = getText(keyshareAttributeElements[0])

    for fn in sorted(os.listdir(path)):
        issuerPath = path + '/' + fn
        if os.path.exists(issuerPath + '/description.xml'):
            schememgr['issuers'][fn] = readIssuer(issuerPath)

    return schememgr


def generateHTML(index, out, lang):
    os.makedirs(out, exist_ok=True)

    render(out + '/index.html', 'about.html',
           index=index,
           LANG=lang,
           identifier='')

    render(out + '/glossary.html', 'glossary.html',
           index=index,
           LANG=lang,
           identifier='glossary')

    for schememgr in index:
        render(out + '/' + schememgr['identifier'] + '.html', 'schememgr.html',
               index=index,
               schememgr=schememgr,
               LANG=lang,
               identifier=schememgr['identifier'])
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
    # TODO: put this in a config file?
    schememanagers = [{
        'source': 'pbdf-schememanager',
        'github': 'https://github.com/privacybydesign/pbdf-schememanager/blob/master'
    }, {
        'source': 'irma-demo-schememanager',
        'github': 'https://github.com/privacybydesign/irma-demo-schememanager/blob/master',
    }]
    index = []
    for info in schememanagers:
        index.append(readSchemeManager(info['source'], info['github']))
    json.dump(index, open('index.json', 'w'))
    
    generateHTML(index, 'en', 'en')
    generateHTML(index, 'nl', 'nl')
