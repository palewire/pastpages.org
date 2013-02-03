var page = require('webpage').create();
var address = phantom.args[0];
var outfile = phantom.args[1];
page.viewportSize = { width: 1024, height: 768 };
page.settings.userAgent = "PastPages.org's pet robot";
page.onLoadFinished = function (status) {
    if (status !== 'success') {
        console.log('Unable to access the network!');
        phantom.exit();
    } else {
        window.setTimeout(function () {
            page.render(outfile);
            phantom.exit();
        }, 200);
    }
};
page.open(address);
