// ==UserScript==
// @name         Pizza zamawianie
// @namespace    http://tampermonkey.net/
// @version      2026-11-03
// @description  -
// @author       Laura
// @match        https://www.pyszne.pl/en/menu/*
// @match        https://www.pyszne.pl/menu/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=pyszne.pl
// @grant        none
// ==/UserScript==


// Polish patterns match word prefixes so they catch every inflection
// (szynka, szynką, szynki). \b is ASCII-only in JS and breaks on ą/ł/ś, hence
// the \p{L} lookbehind.
function polish(...stems) {
    return new RegExp(String.raw`(?<!\p{L})(` + stems.join('|') + ')', 'iu');
}

function english(...words) {
    return new RegExp(String.raw`\b(` + words.join('|') + String.raw`)\b`, 'i');
}

const spicy = [
    polish(
        'jalape[nñ]', 'tabasco', 'chil+i', 'habanero', 'sriracha', 'harissa',
        'peperoncin', 'pepperoncin', 'ostr[yaeąo]', 'pikant', 'piekąc',
        'diabl', 'diavol',
    ),
    english('spicy', 'hot sauce'),
];

const fungi = [
    polish(
        'pieczar', 'grzyb', 'borowik', 'podgrzyb', 'kurk[iaą]', 'boczniak',
        'trufl', 'shiitake', 'portobello',
    ),
    english('mushrooms?', 'champignons?', 'truffles?'),
];

const meat = [
    // meat
    polish(
        'mięs', 'mielon', 'wołow', 'wolow', 'wieprz', 'cielęc', 'jagnię',
        'baran', 'schab', 'karkówk', 'polędwic', 'żeber', 'golonk',
        'kurcz', 'drób', 'drobiow', 'indy[kc]', 'kacz',
        'gęś', String.raw`gęsi(?!\p{L})`, 'gęsin',
        'szyn', 'salam', 'boczek', 'boczk', 'bekon', 'kiełbas', 'kielbas',
        'kabanos', 'parówk', 'parowk', 'chorizo', 'prosciutto', 'pancett',
        'guanciale', 'bresaol', 'nduj', 'salsicc', 'pepperoni', 'mortadel',
        'pastram', 'wędlin', 'pasztet', 'wątrób', 'wątrob',
        'kebab', 'gyros', 'shoarm', 'szaurm', 'szawarm',
    ),
    // fish and seafood
    polish(
        'ryb', 'tuńczyk', 'tunczyk', 'łoso', 'losos', 'dorsz', 'pstrąg',
        'makrel', 'śledź', 'śledzi', 'sardyn', 'anchois', 'morza', 'krewet',
        'małż', 'malż', 'mul[ei]', 'kalmar', 'kałamarnic', 'ośmiorni',
        'homar', 'krab',
    ),
    english(
        'ham', 'bacon', 'pepperoni', 'sausages?', 'chicken', 'turkey', 'duck',
        'beef', 'pork', 'lamb', 'mutton', 'veal', 'meat', 'meatballs?',
    ),
    english(
        'fish', 'tuna', 'salmon', 'anchov(y|ies)', 'shrimps?', 'prawns?',
        'seafood', 'mussels?', 'squid', 'calamari', 'crab', 'lobster', 'octopus',
    ),
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
    [data-qa=item-card].vegeta > div:first-child { background-color: var(--veggie-color) !important; }
    [data-qa=item-card].spicy > div:first-child { background-color: var(--spicy-color) !important; }
    [data-qa=item-card].vegeta.spicy > div:first-child {
        background: repeating-linear-gradient(45deg, var(--spicy-color), var(--spicy-color) 10px, var(--veggie-color) 10px, var(--veggie-color) 20px);
    }
    [data-qa=item-card].fungi:after { position: absolute; bottom: 0; right: 0; content: '🍄'; font-size: 2rem; z-index: 99; }
`;

function getSelector() {
    return '[class*="listItemContent-description"]';
}

function matches(list, text) {
    return list.some(pattern => pattern.test(text));
}

function checkAndMark(element) {
    const cardParent = element.closest('[data-qa="item-card"]');
    if (!cardParent) {
        return;
    }

    if (!matches(meat, element.textContent)) {
        cardParent.classList.add('vegeta');
    }
    if (matches(spicy, element.textContent)) {
        cardParent.classList.add('spicy');
    }
    if (matches(fungi, element.textContent)) {
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
