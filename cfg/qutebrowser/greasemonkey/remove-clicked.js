// ==UserScript==
// @name         remove-clicked
// @description  Remove clicked elements.
// @version      1.0
// @author       rr-
// @include      *
// @require      http://code.jquery.com/jquery-1.8.0.min.js
// @run-at       document-start|document-end
// ==/UserScript==

(function() {
    $(document).click(function (e) {
        if (e.ctrlKey) {
            var element = e.target;
            $(element).remove();
            e.stopPropagation();
            return false;
        }
    });
})();
