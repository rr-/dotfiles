// ==UserScript==
// @name         Pyszne.pl augment
// @namespace    http://tampermonkey.net/
// @version      2024-01-14
// @description  Make thumbnails link to hi-res images. Disable endless scroll
// @author       rr-
// @match        https://www.pyszne.pl/menu/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=pyszne.pl
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  function removeEndlessScroll() {
    if (document.querySelector('head style[data-fix-endless-scroll]')) {
      return;
    }

    const cssString = `
  [data-qa="item-category-list"]>div>div:last-child {
  position: fixed;
  left: 50vw;
  top: 50vh;
  width: 100px;
  height: 100px;
  background: transparent;
  pointer-events: none;
}`;

    const styleElement = document.createElement('style');
    styleElement.innerHTML = cssString;
    styleElement.dataset.fixEndlessScroll = true;
    document.head.appendChild(styleElement);
  }

  function makePictureLinks($root) {
    if (!$root.querySelectorAll) {
      return;
    }

    for (const $imageNode of $root.querySelectorAll(
      '[data-qa="media"] [data-qa="picture"]>img'
    )) {
      const $linkNode = document.createElement('a');
      $linkNode.href = $imageNode.src.replace(/([hw])_\d+/g, '$1_1200');
      $linkNode.target = '_blank';
      $linkNode.addEventListener('click', (e) => handleImageClick(e));
      const $clonedImageNode = $imageNode.cloneNode();
      $linkNode.appendChild($clonedImageNode);
      $imageNode.parentNode.replaceChild($linkNode, $imageNode);
    }
  }

  function handleDOMMutation(mutations) {
    for (const mutation of mutations) {
      for (const $node of mutation.addedNodes) {
        makePictureLinks($node);
      }
    }
    removeEndlessScroll();
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
