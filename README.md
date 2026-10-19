# J.A.R.V.I.S. V18.6.0 – Smart Commands Offline

Bewährte Offline-Basis mit deutscher Befehlsverarbeitung und Android-TTS.

## APK bauen
1. GitHub öffnen und dieses Repository aufrufen.
2. Den Reiter **Actions** öffnen.
3. **J.A.R.V.I.S. Android APK bauen** auswählen.
4. **Run workflow** drücken, falls der Workflow nicht bereits automatisch startet.
5. Nach erfolgreichem Lauf den Bereich **Artifacts** öffnen und `JARVIS-V18.6.0-APK` herunterladen.

## Wichtige Hinweise
- Diese Kivy/Buildozer-Konfiguration ist ein Build-Versuch und muss durch GitHub Actions erfolgreich durchlaufen, bevor eine APK als fertig gelten kann.
- Die ursprüngliche V18.6.0-Datei wird als unveränderte Backup-Datei mitgeliefert.
- Ein dauerhaftes Wakeword bei ausgeschaltetem Bildschirm ist nicht enthalten.
- Die App verwendet Android Text-to-Speech und die eingebauten Befehle funktionieren lokal/offline.
