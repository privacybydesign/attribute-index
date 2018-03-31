'use strict';

const LANG = 'en'; // TODO

const MESSAGES = {
  'en': {
    'yes': 'Yes',
    'no': 'No',
  }
}[LANG];

var data;

function hashchange(e) {
  if (e) {
    document.body.classList.toggle('hide-nav', true); // disable nav on mobile
  }

  var nav = document.querySelector('#nav');
  var main = document.querySelector('#main');
  var hash = document.location.hash;
  if (!hash) {
    hash = '#'; // for consistency
  }

  $('#tree .nav-item a.active').removeClass('active');
  $('#tree .nav-item a[href="' + hash + '"]').addClass('active');

  var parts = hash.substr(1).split('.');
  if (hash === '#') {
    main.innerHTML = document.querySelector('#templates > .page-start').innerHTML;
    var schemeIds = Object.keys(data);
    schemeIds.sort();
    for (var schemeId of schemeIds) {
      var schemeData = data[schemeId];
      main.querySelector('.schememanagers').innerHTML += document.querySelector('#templates > .fragment-schememanager').innerHTML;
      var schememanager = main.querySelector('.schememanagers .schememanager:last-child');
      schememanager.querySelector('.name').innerText = schemeData.name[LANG];
      schememanager.querySelector('.name').setAttribute('href', '#' + schemeId);
      schememanager.querySelector('.description').innerText = schemeData.description[LANG];
    }
  } else if (parts.length == 2) {
    main.innerHTML = document.querySelector('#templates > .page-schememanager').innerHTML;
    var schemeId = parts[0];
    var issuerId = parts[1];
    var schemeManager = data[schemeId];
    var issuer = schemeManager.issuers[schemeId];
    main.querySelector('.name').innerText = issuer.name[LANG];
    main.querySelector('.logo').setAttribute('src', issuer.logo);
    main.querySelector('.path').innerText = schemeId + '.' + issuerId;
    main.querySelector('.description').innerText = schemeManager.description[LANG];
    main.querySelector('.shortName').innerText = issuer.shortName[LANG];
    main.querySelector('.contact a').innerText = schemeManager.contact;
    main.querySelector('.contact a').setAttribute('href', schemeManager.contact);
    main.querySelector('.contactEmail a').innerText = issuer.contactEmail;
    main.querySelector('.contactEmail a').setAttribute('href', 'mailto:' + issuer.contactEmail);
    main.querySelector('.url').innerText = schemeManager.url;
    var credentialIds = Object.keys(issuer.credentials);
    credentialIds.sort();
    for (var credentialId of credentialIds) {
      var credentialData = issuer.credentials[credentialId];
      main.querySelector('.credentials').innerHTML += document.querySelector('#templates > .fragment-credential').innerHTML;
      var credential = main.querySelector('.credentials .credential:last-child');
      credential.querySelector('.name').innerText = credentialData.name[LANG];
      credential.querySelector('.name').setAttribute('href', '#' + schemeId + '.' + issuerId + '.' + credentialId);
      credential.querySelector('.description').innerText = credentialData.description[LANG];
    }
  } else if (parts.length == 3) {
    main.innerHTML = document.querySelector('#templates > .page-credential').innerHTML;
    var schemeId = parts[0];
    var issuerId = parts[1];
    var credentialId = parts[2];
    var credential = data[schemeId].issuers[issuerId].credentials[credentialId];
    main.querySelector('.name').innerText = credential.name[LANG];
    main.querySelector('.path').innerText = parts.join('.');
    main.querySelector('.logo').setAttribute('src', credential.logo);
    main.querySelector('.description').innerText = credential.description[LANG];
    main.querySelector('.shortName').innerText = credential.shortName[LANG];
    main.querySelector('.singleton').innerText = MESSAGES[credential.shouldBeSingleton ? 'yes' : 'no'];
    for (var attribute of credential.attributes) {
      main.querySelector('.attributes').innerHTML += document.querySelector('#templates > .fragment-attribute').innerHTML;
      var element = main.querySelector('.attribute:last-child');
      element.querySelector('.name').innerText = attribute.name[LANG];
      element.querySelector('.path').innerText = parts.join('.') + '.' + attribute.id;
      element.querySelector('.description').innerText = attribute.description[LANG];
    }
  } else {
    console.error('unknown hash:', hash);
    main.innerHTML = ''; // TODO: show 404 or something
  }
}

function buildMenuTree() {
  var tree = document.querySelector('#tree');
  tree.appendChild(document.querySelector('#templates > .treenode-about').children[0].cloneNode(true));
  for (var schemeId in data) {
    var schemeData = data[schemeId];
    for (var issuerId in schemeData.issuers) {
      var issuerData = schemeData.issuers[issuerId];
      var rootItem = document.querySelector('#templates > .treenode-schememanager').children[0].cloneNode(true);
      tree.appendChild(rootItem);
      var rootEl = rootItem.querySelector('.nav-link');
      rootEl.innerText = issuerData.shortName[LANG];
      rootEl.setAttribute('title', issuerData.name[LANG]);
      rootEl.setAttribute('href', '#' + schemeId + '.' + issuerId);
      var ids = Object.keys(issuerData.credentials);
      ids.sort();
      for (var credentialId of ids) {
        var credentialData = issuerData.credentials[credentialId];
        rootItem.innerHTML += document.querySelector('#templates > .treenode-credential').innerHTML;
        var credentialEl = rootItem.querySelector('.credential:last-child');
        credentialEl.querySelector('a').innerText = credentialData.shortName[LANG];
        credentialEl.querySelector('a').setAttribute('title', credentialData.name[LANG]);
        credentialEl.querySelector('a').setAttribute('href', '#' + schemeId + '.' + issuerId + '.' + credentialId);
      }
    }
  }
  //$('[data-toggle="tooltip"]', tree).tooltip()
  hashchange();
  window.onhashchange = hashchange;
}

function doSearch(e) {
  var string = e.target.value;
  $('#tree > li:not(.search)').remove();
  if (!string) {
    buildMenuTree();
    return;
  }

  // now find all matching credentials/attributes
}

function init() {
  document.querySelector('.toggle-nav').onclick = function(e) {
    e.preventDefault();
    document.body.classList.toggle('hide-nav');
  };

  document.querySelector('.search').oninput = doSearch;

  var req = new XMLHttpRequest();
  req.open('GET', 'data.json');
  req.send();
  req.onload = function(e) {
    data = JSON.parse(req.responseText);
    buildMenuTree();
  }
}

init();
