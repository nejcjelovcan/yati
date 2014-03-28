(function (window) {
    "use strict";
    var events = Object.create(window.Backbone.Events);
    (window.yati && window._(window.yati).extend(events)) || (window.yati = events);
}(window));