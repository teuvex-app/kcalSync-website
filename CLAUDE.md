# CLAUDE.md

Hinweise für Claude Code in diesem Repository.

## Sicherheitsprüfung und Abhängigkeiten (Stand 18.10.2026)

**Semgrep läuft bei jedem Push** (`.github/workflows/semgrep-audit.yml`, Regelsätze
`p/default` und `p/secrets`, ohne Metriken). Der Lauf wird **rot**, sobald es einen Fund
gibt, der nicht in `.github/semgrep-geprueft.json` steht. Die Ergebnisse stehen auf der
Ergebnisseite des Laufs (Actions → semgrep-audit → Summary).

- Einen roten Lauf nicht durch Abschalten, `continue-on-error` oder Lockern der Auswertung
  beheben. Echte Funde werden im Code behoben.
- Nachweislich harmlose Funde kommen in `.github/semgrep-geprueft.json`: Datei, Regel, ein
  Merkmal der Stelle (`enthaelt`) und eine nachvollziehbare Begründung. Ein Eintrag gilt nur
  für genau diese Stelle; keine Sammel-Einträge ohne `enthaelt`. Im Zweifel den Nutzer fragen.
- Nicht auf `--config auto` zurückstellen: das geht nur mit eingeschalteten Metriken und
  bricht mit `--metrics=off` ab (so war der Scan bis 18.10.2026 dauerhaft kaputt).

**GitHub Actions** werden nur mit fester Commit-Kennung eingebunden, die Version steht als
Kommentar daneben (`uses: actions/checkout@<40 Zeichen> # v4.4.0`), nie mit `@v4` oder
`@main`. Dependabot hält die Kennungen aktuell.

**Dependabot** schlägt neue Fassungen erst nach 7 Tagen vor (`cooldown` in
`.github/dependabot.yml`) - Schutz vor frisch veröffentlichten Schadpaketen;
Sicherheitsupdates kommen trotzdem sofort. Die Wartezeit nicht entfernen.
