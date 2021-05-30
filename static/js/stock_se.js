document.getElementById("openLinkBtn").addEventListener("click", openLink);
function openLink() {
  var link = document.getElementById("myLink").value;
  openInNewTab("http://127.0.0.1:8000/stock/" + link );
}
function openInNewTab(url) {
  var win = window.open(url, '_blank');
  win.focus();
}