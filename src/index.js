'use strict';

const irma = require('@privacybydesign/irma-frontend');

const LANG = document.getElementsByTagName("html")[0].getAttribute("lang");
const MAX_SEARCH = 8; // max number of search results in the results dropdown
const IRMA_SERVER = 'https://demo.privacybydesign.foundation/backend';

var index;

function searchChange(e) {
  var string = e.target.value.toLowerCase();
  var searchresults = document.querySelector('#searchresults');
  searchresults.innerHTML = '';

  // Create a Bootstrap 5 dropdown instance if it doesn't exist
  var dropdown = bootstrap.Dropdown.getOrCreateInstance(e.target);
  
  if (string) {
    dropdown.show();
  } else {
    dropdown.hide();
    return;
  }

  // Now find all matching credentials/attributes.
  var numFound = doSearch(searchresults, string);
  if (numFound == 0) {
    searchresults.appendChild(document.querySelector('#templates .no-searchresult').cloneNode(true));
  }
}

function doSearch(searchresults, string) {
    // Keep track of seen paths and count
    const seen = new Set();
    let count = 0;

    // Iterate through the index
    for (const schememgr of index) {
        const issuerKeys = Object.keys(schememgr.issuers).sort();
        
        for (const issuerId of issuerKeys) {
            const issuer = schememgr.issuers[issuerId];
            const credentialKeys = Object.keys(issuer.credentials).sort();
            
            for (const credentialId of credentialKeys) {
                const credential = issuer.credentials[credentialId];
                
                for (const attribute of credential.attributes) {
                    // Check if attribute matches search string
                    if (attribute.identifier.toLowerCase().includes(string) || 
                        attribute.name[LANG].toLowerCase().includes(string)) {
                        
                        // Skip if we've seen this attribute before
                        if (seen.has(attribute.identifier)) continue;
                        seen.add(attribute.identifier);
                        count++;

                        // Create search result element
                        const el = document.querySelector('#templates > .searchresult').cloneNode(true);
                        el.href = `${credential.identifier}.html#${attribute.identifier}`;
                        el.querySelector('.credential').textContent = credential.name[LANG];
                        el.querySelector('.attribute').textContent = attribute.name[LANG];
                        el.querySelector('.identifier').textContent = attribute.identifier;
                        searchresults.appendChild(el);

                        // Stop if we've reached the maximum number of results
                        if (count >= MAX_SEARCH) return count;
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

  // Issue, by showing a popup.
  const request = {
    '@context': 'https://irma.app/ld/request/issuance/v2',
    'credentials': [
      {
        'credential': credentialID,
        'attributes': attributes,
      },
    ]
  };

  var credtype = findCredType(credentialID);
  if (credtype && credtype.revocation)
    request.credentials[0].revocationKey = revocationKey();
  console.log('issuing test attributes:', request);

  irma.newPopup({
    session: {
      url: IRMA_SERVER,
      start: {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      }
    },
  })
  .start()
  .then(() => {
    console.log("Issuance successful");
    if (!credtype.revocation) return;
    document.getElementById("issue-alert").style.display = "";
    document.getElementById("revocation-key").innerHTML = request.credentials[0].revocationKey;
  })
  .catch(error => console.error("Issuance failed: ", error));
}

// Construct a random string of 10 characters
function revocationKey() {
  return [...Array(10)].map(() => Math.random().toString(36)[2]).join('');
}

function findCredType(credentialID) {
  var parts = credentialID.split(".");

  for (var schemeid in index) {
    var scheme = index[schemeid];
    if (scheme.id === parts[0]) {
      if (!scheme.issuers[parts[1]])
        return null;
      return scheme.issuers[parts[1]].credentials[parts[2]];
    }
  }

  return null;
}

function init() {
 
  document.querySelector('.dropdown input[type=search]').oninput = searchChange;

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
