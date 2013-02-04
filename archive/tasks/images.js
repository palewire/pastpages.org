var page = require('webpage').create();
var address = phantom.args[0];
var outfile = phantom.args[1];
var secondsToWait = 2;
page.viewportSize = { width: 1024, height: 768 };
page.open(address, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit();
    } else {
        window.setTimeout(function () {
            page.render(outfile);
            phantom.exit();
        }, secondsToWait * 100);
    }
});
