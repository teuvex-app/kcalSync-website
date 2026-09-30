// Schutz gegen das Einbetten dieser Seite in einen fremden Rahmen (Clickjacking).
//
// Ueblich waere dafuer die Kopfzeile X-Frame-Options oder die CSP-Anweisung
// frame-ancestors. Beides setzt einen Server voraus, der eigene Kopfzeilen
// mitschickt. Diese Seite liegt auf GitHub Pages, und dort ist das nicht
// moeglich: Die Kopfzeilen in firebase.json werden nicht mehr gelesen, seit die
// Auslieferung ueber den Zweig gh-pages laeuft. In einem <meta>-Element wird
// frame-ancestors von den Browsern ausdruecklich ignoriert.
//
// Bleibt dieser Weg: Merkt die Seite, dass sie nicht das oberste Fenster ist,
// ersetzt sie das oberste Fenster durch sich selbst. Das ist schwaecher als
// eine Kopfzeile - ein Rahmen mit sandbox="allow-scripts" ohne
// allow-top-navigation kann es unterbinden - aber es nimmt den einfachen Fall
// weg, dass jemand teuvex.de als Kulisse hinter eigene Schaltflaechen legt.
(function () {
  try {
    if (window.self !== window.top) {
      window.top.location = window.self.location;
    }
  } catch (e) {
    // Zugriff auf window.top verweigert - dann sind wir sicher eingebettet.
    document.documentElement.style.display = 'none';
    window.location = window.self.location;
  }
})();
