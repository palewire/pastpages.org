var page = require('webpage').create();
var address = phantom.args[0];
var outfile = phantom.args[1];
var secondsToWait = 15;
page.settings.userAgent = 'PastPages: The News Homepage Archive (www.pastpages.org)';
page.viewportSize = { width: 1024, height: 768 };
page.evaluate(function() {
    document.body.bgColor = 'white';
});
page.open(address, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit();
    } else {
        if (
            address.substring(0, "http://www.latimes.com/".length) === "http://www.latimes.com/" ||
            address.substring(0, "http://www.chicagotribune.com/".length) === "http://www.chicagotribune.com/" ||
            address.substring(0, "http://www.baltimoresun.com/".length) === "http://www.baltimoresun.com/" ||
            address.substring(0, "http://www.dailypress.com/".length) === "http://www.dailypress.com/" ||
            address.substring(0, "http://www.courant.com/".length) === "http://www.courant.com/" ||
            address.substring(0, "http://www.mcall.com/".length) === "http://www.mcall.com/" ||
            address.substring(0, "http://www.sun-sentinel.com/".length) === "http://www.sun-sentinel.com/" ||
            address.substring(0, "http://www.orlandosentinel.com/".length) === "http://www.orlandosentinel.com/"
           ) {
            console.log("Setting custom Tribune NGUX cookie");
            var d = page.evaluate(function() {
                window.sessionStorage.setItem('trb.browsersupport.supported', 'true');
            });
            page.reload();
        }
        page.evaluate(function() {
          var style = document.createElement('style'),
              text = document.createTextNode('body { background: #fff }');
          style.setAttribute('type', 'text/css');
          style.appendChild(text);
          document.head.insertBefore(style, document.head.firstChild);
          //window.document.body.scrollTop = document.body.scrollHeight;
        });
        window.setTimeout(function () {
            if (getComputedStyle(document.body, null).backgroundColor === 'rgba(0, 0, 0, 0)') {
              console.log("Setting background color to white");
              document.body.bgColor = '#ffffff';
            }
            page.render(outfile);
            phantom.exit();
        }, secondsToWait * 1000);
    }
});
