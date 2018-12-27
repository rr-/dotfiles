// ==UserScript==
// @name         remove-clicked
// @description  Remove clicked elements.
// @version      1.0
// @author       rr-
// @include      *
// @run-at       document-start|document-end
// ==/UserScript==

(function() {
    document.addEventListener('click', function (event) {
        if (event.ctrlKey) {
            var element = event.target;
            element.parentNode.removeChild(element);
            event.stopPropagation();
            return false;
        }
    });
})();
