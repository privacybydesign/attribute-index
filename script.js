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
  } else if (parts.length == 1) {
    main.innerHTML = document.querySelector('#templates > .page-schememanager').innerHTML;
    var schemeId = parts[0];
    var root = data[schemeId];
    main.querySelector('.name').innerText = root.name[LANG];
    main.querySelector('.logo').setAttribute('src', root.logo);
    main.querySelector('.path').innerText = schemeId;
    main.querySelector('.description').innerText = root.description[LANG];
    main.querySelector('.shortName').innerText = root.shortName[LANG];
    main.querySelector('.contact a').innerText = root.contact;
    main.querySelector('.contact a').setAttribute('href', root.contact);
    main.querySelector('.contactEmail a').innerText = root.contactEmail;
    main.querySelector('.contactEmail a').setAttribute('href', root.contactEmail);
    main.querySelector('.url').innerText = root.url;
    var credentialIds = Object.keys(root.credentials);
    credentialIds.sort();
    for (var credentialId of credentialIds) {
      var credentialData = root.credentials[credentialId];
      main.querySelector('.credentials').innerHTML += document.querySelector('#templates > .fragment-credential').innerHTML;
      var credential = main.querySelector('.credentials .credential:last-child');
      credential.querySelector('.name').innerText = credentialData.name[LANG];
      credential.querySelector('.name').setAttribute('href', '#' + schemeId + '.' + credentialId);
      credential.querySelector('.description').innerText = credentialData.description[LANG];
    }
  } else if (parts.length == 2) {
    main.innerHTML = document.querySelector('#templates > .page-credential').innerHTML;
    var credential = data[parts[0]].credentials[parts[1]];
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
    var rootItem = document.querySelector('#templates > .treenode-schememanager').children[0].cloneNode(true);
    tree.appendChild(rootItem);
    var rootEl = rootItem.querySelector('.nav-link');
    rootEl.innerText = schemeData.shortName[LANG];
    rootEl.setAttribute('title', schemeData.name[LANG]);
    rootEl.setAttribute('href', '#' + schemeId);
    var ids = Object.keys(schemeData.credentials);
    ids.sort();
    for (var credentialId of ids) {
      var credentialData = schemeData.credentials[credentialId];
      rootItem.innerHTML += document.querySelector('#templates > .treenode-credential').innerHTML;
      var credentialEl = rootItem.querySelector('.credential:last-child');
      credentialEl.querySelector('a').innerText = credentialData.shortName[LANG];
      credentialEl.querySelector('a').setAttribute('title', credentialData.name[LANG]);
      credentialEl.querySelector('a').setAttribute('href', '#' + schemeId + '.' + credentialId);
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
