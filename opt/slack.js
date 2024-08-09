// ==UserScript==
// @name         Slack declutter
// @version      2024-08-09
// @description  Improve appearance of Slack
// @author       rr-
// @match        https://app.slack.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=slack.com
// @grant        GM_addStyle
// ==/UserScript==

(function () {
  "use strict";

  GM_addStyle(
    `
        .p-ia4_client .p-client_workspace_wrapper {
           grid-template: "p-client-workspace" / auto;
           grid-template-columns: 1fr !important;
        }
        .p-tab_rail {
          display: none !important;
        }
        .p-ia4_client--narrow-feature-on .p-control_strip {
          width: 60px !important;
          margin-bottom: 15px !important;
        }
        `,
  );
})();
