"use strict";

var Django = window.Django || {};

$(function() {
  Django.Csrf.init();
  Django.Data.init();
});
