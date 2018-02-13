'use strict';

document.querySelectorAll('[data-drilldown]').forEach(element => {
    new Foundation.Drilldown($j(element), {});
});
