#!/usr/bin/python3

import json
from xml.dom import minidom
import os

BOOL = {
    'true': True,
    'false': False,
}

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

def readCredential(path):
    xml = minidom.parse(path + '/description.xml')
    credential = {
        'name':              translated(xml.getElementsByTagName('Name')[0]),
        'shortName':         translated(xml.getElementsByTagName('ShortName')[0]),
        'description':       translated(xml.getElementsByTagName('Description')[0]),
        'shouldBeSingleton': BOOL[getText(xml.getElementsByTagName('ShouldBeSingleton')[0])],
        'logo':              path + '/logo.png',
        'attributes':        [],
    }

    for attribute in xml.getElementsByTagName('Attributes')[0].childNodes:
        if attribute.nodeType != attribute.ELEMENT_NODE:
            continue
        credential['attributes'].append({
            'id':          attribute.getAttribute('id'),
            'name':        translated(attribute.getElementsByTagName('Name')[0]),
            'description': translated(attribute.getElementsByTagName('Description')[0]),
        })

    return credential

def makeIndex(path):
    index = {}

    xml = minidom.parse(path + '/description.xml')
    id = getText(xml.getElementsByTagName('Id')[0])
    index = {
        'name':        translated(xml.getElementsByTagName('Name')[0]),
        'description': translated(xml.getElementsByTagName('Description')[0]),
        'url':         getText(xml.getElementsByTagName('Url')[0]),
        'contact':     getText(xml.getElementsByTagName('Contact')[0]),
    }

    xml = minidom.parse(path + '/' + id + '/description.xml')
    index['shortName'] = translated(xml.getElementsByTagName('ShortName')[0])
    index['contactEmail'] = getText(xml.getElementsByTagName('ContactEMail')[0])
    index['logo'] = path + '/' + id + '/logo.png'
    index['credentials'] = {}

    for fn in sorted(os.listdir(path + '/' + id + '/Issues')):
        index['credentials'][fn] = readCredential(path + '/' + id + '/Issues/' + fn)

    return id, index


if __name__ == '__main__':
    schememanagers = ['pbdf-schememanager']
    index = {}
    for path in schememanagers:
        id, data = makeIndex(path)
        index[id] = data
    json.dump(index, open('data.json', 'w'))
