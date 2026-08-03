// ==UserScript==
// @name         Pizza zamawianie
// @namespace    http://tampermonkey.net/
// @version      2025-08-09
// @description  -
// @author       Laura
// @match        https://www.pyszne.pl/en/menu/*
// @match        https://www.pyszne.pl/menu/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=pyszne.pl
// @grant        none
// ==/UserScript==


const spicy = [
    'jalapeno',
    'tabasco',
    'chili',
    'chilli',
];

const fungi = [
    'pieczar',
];

const meat = [
    'kebab',
    'szynka',
    'szynką',
    'salami',
    'boczek',
    'boczkiem',
    'kiełbas',
    'kabanos',
    'shoarma',
    'shoarmą',
    'tuńczyk',
    'morza',
    'małż',
    'krewetk',
    'kurczak',
    'bacon',
    'bekon',
    'ham',
    'mięso',
    'wieprz',
    'woło',
    'chorizo',
    'parówk',
    'prosciutto',
    'łoso',
    'mielone',
    'gyros',
];

const css = `
    :root {
        --veggie-color: #ccffaa;
        --spicy-color: #ffccaa;
    }
    html[data-color-mode=dark] {
        --veggie-color: #1b6301;
        --spicy-color: #631b01;
    }
    [data-qa=card].vegeta span:empty { background-color: var(--veggie-color) !important; }
    [data-qa=card].spicy span:empty { background-color: var(--spicy-color) !important; }
    [data-qa=card].vegeta.spicy span:empty {
        background: repeating-linear-gradient(45deg, var(--spicy-color), var(--spicy-color) 10px, var(--veggie-color) 10px, var(--veggie-color) 20px);
    }
    [data-qa=card].fungi:after { position: absolute; bottom: 0; right: 0; content: '🍄'; font-size: 2rem; z-index: 99; }
`;

function getSelector() {
    return '[class*="list-item-content-style_item-description"]';
}

function checkAndMark(element) {
    const cardParent = element.closest('[data-qa="card"]');
    if (!cardParent) {
        return;
    }

    if (!meat.some(item => element.textContent.includes(item))) {
        cardParent.classList.add('vegeta');
    }
    if (spicy.some(item => element.textContent.includes(item))) {
        cardParent.classList.add('spicy');
    }
    if (fungi.some(item => element.textContent.includes(item))) {
        cardParent.classList.add('fungi');
    }
}

(function() {
    'use strict';

    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                document.querySelectorAll(getSelector()).forEach(checkAndMark);
            });
        });
    });
    // Observe the docment body for subtree changes
    observer.observe(document.body, { childList: true, subtree: true });
    // Initial check for already existing nodes
    document.querySelectorAll(getSelector()).forEach(checkAndMark);

    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
})();
