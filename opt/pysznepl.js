// ==UserScript==
// @name         Pyszne.pl augment
// @namespace    http://tampermonkey.net/
// @version      2024-01-14
// @description  Link to hi-res thumbnails
// @author       rr-
// @match        https://www.pyszne.pl/menu/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=pyszne.pl
// @grant        none
// ==/UserScript==

(function () {
  "use strict";

  function makePictureLinks($root) {
    for (const $imageNode of $root.querySelectorAll(
      ':is([data-qa="item-category-list"], [data-qa="popular-items-list"]) [data-qa="picture"]>img',
    )) {
      const $linkNode = document.createElement("a");
      $linkNode.href = $imageNode.src.replace(/([hw])_\d+/g, "$1_1200");
      $linkNode.target = "_blank";
      $linkNode.addEventListener("click", (e) => handleImageClick(e));
      const $clonedImageNode = $imageNode.cloneNode();
      $linkNode.appendChild($clonedImageNode);
      $imageNode.parentNode.replaceChild($linkNode, $imageNode);
    }
  }

  function handleDOMMutation(mutations) {
    for (const mutation of mutations) {
      for (const $node of mutation.addedNodes) {
        if ($node.querySelectorAll) {
          makePictureLinks($node);
        }
      }
    }
  }

  function handleImageClick(e) {
    e.stopPropagation();
  }

  const observer = new MutationObserver(handleDOMMutation);
  observer.observe(document, {
    childList: true,
    subtree: true,
    attributes: false,
  });
})();
