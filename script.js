'use strict';

var data;

function doSearch(e) {
  var string = e.target.value;
  document.body.classList.toggle('in-search', string.length != 0);
  if (!string) {
    return;
  }

  // now find all matching credentials/attributes
}

function init() {
  document.querySelector('.toggle-nav').onclick = function(e) {
    e.preventDefault();
    document.body.classList.toggle('show-nav');
  };

  document.querySelector('.search').oninput = doSearch;

  var req = new XMLHttpRequest();
  req.open('GET', INDEX_URL);
  req.send();
  req.onload = function(e) {
    data = JSON.parse(req.responseText);
  }

  //$('[data-toggle="tooltip"]', tree).tooltip()
}

init();
