**Beschreibung:**
Einstellungsseite für AWS Connection, Benachrichtigungen und Account.

**Aufgaben:**
- ✅ AWS Connection: Status Badge (grün/rot), Account ID, Region, Last Sync, "Update Credentials" Button, "Disconnect" Button (rot), "Sync Now" Button
- ✅ Notifications: Toggles für Anomalie-Alerts, Weekly Report, Neue Empfehlungen, E-Mail-Feld
- ✅ Account: Name, E-Mail (read-only mit Edit), "Delete Account" (rot, mit Bestätigungs-Modal)

**Akzeptanzkriterien:**
- [x] Connection Status zeigt korrekten State (Connected/Disconnected)
- [x] Toggles speichern den Status (API oder lokal)
- [x] "Disconnect" zeigt Bestätigungs-Dialog
- [x] "Sync Now" triggert eine sofortige Datenaktualisierung

**Implementierungsdetails:**
- Backend: GET /api/accounts/{account_id} endpoint für Account-Details
- Backend: PATCH /api/accounts/{account_id}/credentials endpoint für Credential-Updates
- Frontend: useAccount Hook erweitert mit region, email, lastSynced
- Frontend: useNotificationSettings Hook für Notification-Toggle-Persistierung
- Frontend: Settings.tsx komplett überarbeitet mit alle Features, Dialoge, und shadcn-Komponenten
- Frontend: Onboarding.tsx aktualisiert um region beim Connect zu übergeben