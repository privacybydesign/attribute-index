'use strict';

const LANG = 'en'; // TODO
const MAX_SEARCH = 8; // max number of search results in the results dropdown
const IRMA_SERVER = 'https://metrics.privacybydesign.foundation/irmaserver'
const IRMA_AUTHMETHOD = 'none';
const IRMA_KEY = '';
const IRMA_REQUESTORNAME = '';

var index;

function searchChange(e) {
  var string = e.target.value.toLowerCase();
  var searchresults = document.querySelector('#searchresults');
  searchresults.innerHTML = '';
  if (searchresults.classList.contains('show') != (string != '')) {
    // Ugly hack: use a fake button click to show the search results.
    document.querySelector('.search button.dropdown-toggle').click();
  }

  if (!string) {
    return;
  }

  // Now find all matching credentials/attributes.
  var numFound = doSearch(searchresults, string);
  if (numFound == 0) {
    searchresults.appendChild(document.querySelector('#templates .no-searchresult').cloneNode(true));
  }
}

function doSearch(searchresults, string) {
  // This is a very simple search algorithm, but should get the job done.
  // It searches in the attribute identifier and name.
  var seen = {}; // set of paths that have been seen
  var count = 0;
  for (var schememgr of index) {
    var issuerKeys = Object.keys(schememgr.issuers);
    issuerKeys.sort();
    for (var i=0; i<issuerKeys.length; i++) {
      var issuer = schememgr.issuers[issuerKeys[i]];
      var credentialKeys = Object.keys(issuer.credentials);
      credentialKeys.sort();
      for (var j=0; j<credentialKeys.length; j++) {
        var credential = issuer.credentials[credentialKeys[j]];
        for (var attribute of credential.attributes) {
          if (attribute.identifier.toLowerCase().indexOf(string) >= 0 || attribute.name[LANG].toLowerCase().indexOf(string) >= 0) {
            seen[attribute.identifier] = null; // insert into set
            count++;
            var el = document.querySelector('#templates > .searchresult').cloneNode(true);
            el.setAttribute('href', credential.identifier + '.html#' + attribute.identifier);
            el.querySelector('.credential').textContent = credential.name[LANG];
            el.querySelector('.attribute').textContent = attribute.name[LANG];
            el.querySelector('.identifier').textContent = attribute.identifier;
            searchresults.appendChild(el);

            if (count >= MAX_SEARCH) {
              return count;
            }
          }
        }
      }
    }
  }

  return count;
}

// Manually issue a test credential.
function issue(e) {
  e.preventDefault();
  var form = e.target;

  // Load the credential ID from the form.
  var credentialID = form.dataset.credential;

  // Load the attributes from the form.
  var attributes = {};
  var inputs = form.querySelectorAll('input');
  for (var i=0; i<inputs.length; i++) {
    var input = inputs[i];
    attributes[input.dataset.attribute] = input.value;
  }

  // Build the request.
  var request = {
    type: 'issuing',
    credentials: [
      {
        credential: credentialID,
        attributes: attributes,
      },
    ]
  };

  // Issue, by showing a popup.
  console.log('issuing test attributes:', request);
  irma.startSession(IRMA_SERVER, request, IRMA_AUTHMETHOD, IRMA_KEY, IRMA_REQUESTORNAME)
    .then(function(pkg) {
      return irma.handleSession(pkg.sessionPtr, {server: IRMA_SERVER, token: pkg.token, method: 'popup', language: LANG});
    }).then(function(result) {
      console.log('test attributes issued:', result);
      return result;
    }).catch(function(err) {
      console.error('failed to issue test attributes:', err);
    });
}

function init() {
  document.querySelector('.toggle-nav').onclick = function(e) {
    e.preventDefault();
    document.body.classList.toggle('show-nav');
  };

  document.querySelector('input[type=search]').oninput = searchChange;

  var forms = document.querySelectorAll('form.diy-credential');
  for (var i=0; i<forms.length; i++) {
    forms[i].onsubmit = issue;
  }

  var req = new XMLHttpRequest();
  req.open('GET', INDEX_URL);
  req.send();
  req.onload = function(e) {
    index = JSON.parse(req.responseText);
  }

  //$('[data-toggle="tooltip"]', tree).tooltip()
}

init();
