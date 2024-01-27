javascript:(function() {
  const title = document.title || "[untitled page]";
  const body = function () {var html = ""; if (typeof window.getSelection != "undefined") {var sel = window.getSelection(); if (sel.rangeCount) {var container = document.createElement("div"); for (var i = 0, len = sel.rangeCount; i < len; ++i) {container.appendChild(sel.getRangeAt(i).cloneContents());} html = container.innerHTML;}} else if (typeof document.selection != "undefined") {if (document.selection.type == "Text") {html = document.selection.createRange().htmlText;}} var relToAbs = function (href) {var a = document.createElement("a"); a.href = href; var abs = a.protocol + "//" + a.host + a.pathname + a.search + a.hash; a.remove(); return abs;}; var elementTypes = [['a', 'href'], ['img', 'src']]; var div = document.createElement('div'); div.innerHTML = html; elementTypes.map(function(elementType) {var elements = div.getElementsByTagName(elementType[0]); for (var i = 0; i < elements.length; i++) {elements[i].setAttribute(elementType[1], relToAbs(elements[i].getAttribute(elementType[1])));}}); return div.innerHTML;}();
  const url = 'http://{HOST}/capture?password={PASSWORD}&template=w&url=' + encodeURIComponent(location.href) + '&title=' + encodeURIComponent(title) + '&body=' + encodeURIComponent(body);
  console.log(url);
  const oldUrl = location.href;
  location.href = url;
  window.setTimeout(function() {location.href = oldUrl;}, 500);
})()
