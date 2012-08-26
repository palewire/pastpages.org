var page = new WebPage();
var address = phantom.args[0];
var outfile = phantom.args[1];
//var width = 1024;
//var height = 800;
//page.viewportSize = { width: width, height: height };
page.open(address, function (status) {
  if (status !== 'success') {
    phantom.exit(1);
  } else {
    page.render(outfile);
    phantom.exit();
  }
});



//(function() {
//  var filename, page, renderFunction, url, _ref;
//  page = new WebPage();
//  //
//  if (phantom.args.length !== 2) {
//    console.log('Usage: images.js URL filename');
//    phantom.exit();
//  }
//  _ref = phantom.args, url = _ref[0], filename = _ref[1];
//  renderFunction = function() {
//    page.render(filename);
//    console.log(filename);
//    return phantom.exit();
//  };
//  page.open(url, function(status) {
//    if (status !== 'success') {
//      console.log("An error occurred. Status: " + status);
//    }
//    return window.setTimeout(renderFunction, 5000);
//  });
//}).call(this);
