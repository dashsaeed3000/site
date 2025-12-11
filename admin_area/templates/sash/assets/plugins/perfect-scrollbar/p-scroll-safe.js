(function($) {
    "use strict";

    // P-scrolling: only initialize if element exists and PerfectScrollbar is available
    try {
        var docNav = document.querySelector('#documenter_nav');
        if (docNav && typeof PerfectScrollbar !== 'undefined') {
            new PerfectScrollbar(docNav, {
                useBothWheelAxes: true,
                suppressScrollX: true,
            });
        }
    } catch (e) {
        if (window && window.console) console.warn('PerfectScrollbar init skipped:', e);
    }

})(jQuery);
