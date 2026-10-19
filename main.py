# V18.6.0 – J.A.R.V.I.S. Smart Commands Offline für Pydroid 3
# Baut auf der funktionierenden V18.6.0 auf: ergänzt Uhr/Wecker, Kalender und Telefon-Wählbildschirm.
# Die Originaldateien bleiben unverändert.
# Kein Internet für die eingebauten Befehle erforderlich.
# Hinweis: Mikrofon-Wakeword ist hier bewusst noch nicht enthalten, da Pydroid auf dem
# bisherigen Gerät keine Mikrofonberechtigung angeboten hat.

from datetime import datetime
import re

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.core.window import Window

KV = r"""
BoxLayout:
    orientation: 'vertical'
    padding: '16dp'
    spacing: '10dp'
    canvas.before:
        Color:
            rgba: 0.025, 0.055, 0.09, 1
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: '[b]J.A.R.V.I.S.[/b]\\n[b]SMART COMMANDS OFFLINE  V18.6.0[/b]'
        markup: True
        font_size: '24sp'
        color: 0.25, 0.85, 1, 1
        size_hint_y: None
        height: '76dp'
    Label:
        text: root.status_text if hasattr(root, 'status_text') else 'Bereit, Sir.'
        color: 0.78, 0.9, 1, 1
        size_hint_y: None
        height: '34dp'
    TextInput:
        id: command_input
        hint_text: 'Befehl eingeben, z. B. Wie ist mein Akkustand?'
        multiline: False
        size_hint_y: None
        height: '52dp'
        font_size: '17sp'
        on_text_validate: app.run_command()
    Button:
        text: 'BEFEHL AUSFÜHREN'
        size_hint_y: None
        height: '50dp'
        background_normal: ''
        background_color: 0.02, 0.35, 0.52, 1
        on_release: app.run_command()
    Button:
        text: 'ANTWORT SPRECHEN'
        size_hint_y: None
        height: '46dp'
        background_normal: ''
        background_color: 0.04, 0.22, 0.34, 1
        on_release: app.speak_answer()
    Button:
        text: 'OFFLINE-BEFEHLE ANZEIGEN'
        size_hint_y: None
        height: '46dp'
        background_normal: ''
        background_color: 0.04, 0.22, 0.34, 1
        on_release: app.show_help()
    ScrollView:
        do_scroll_x: False
        Label:
            id: answer_label
            text: 'Bereit, Sir. Geben Sie einen Befehl ein.'
            markup: True
            color: 0.9, 0.96, 1, 1
            text_size: self.width, None
            size_hint_y: None
            height: self.texture_size[1] + dp(24)
            halign: 'left'
            valign: 'top'
"""

class JarvisOfflinePlus(App):
    answer = "Bereit, Sir."
    tts = None
    tts_ready = False

    def build(self):
        self.root = Builder.load_string(KV)
        Window.clearcolor = (0.025, 0.055, 0.09, 1)
        self.init_tts()
        return self.root

    def init_tts(self):
        if platform != "android":
            self.answer = "Android-TTS ist nur auf Android verfügbar."
            self.set_answer(self.answer)
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            Locale = autoclass('java.util.Locale')
            self.tts = TextToSpeech(PythonActivity.mActivity, None)
            self.Locale = Locale
            self.TextToSpeech = TextToSpeech
            self.tts.setLanguage(Locale.GERMAN)
            self.tts_ready = True
        except Exception as exc:
            self.tts = None
            self.tts_ready = False
            self.answer = "Sprachausgabe konnte nicht gestartet werden. Prüfen Sie Pydroid und Android-TTS."
            self.set_answer(self.answer)

    def set_answer(self, text):
        self.answer = text
        if self.root:
            self.root.ids.answer_label.text = text

    def speak_answer(self):
        if self.tts_ready and self.tts is not None:
            try:
                self.tts.speak(self.answer, self.TextToSpeech.QUEUE_FLUSH, None)
            except Exception:
                self.set_answer(self.answer + "\n\n[Sprachausgabe gerade nicht verfügbar.]")
        else:
            self.set_answer(self.answer + "\n\n[Android-TTS ist nicht verfügbar.]")

    def get_battery_info(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            IntentFilter = autoclass('android.content.IntentFilter')
            BatteryManager = autoclass('android.os.BatteryManager')

            activity = PythonActivity.mActivity
            intent = activity.registerReceiver(
                None, IntentFilter(Intent.ACTION_BATTERY_CHANGED)
            )
            if intent is None:
                return "Sir, der Akkustand konnte gerade nicht ausgelesen werden."
            level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, 100)
            status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
            plugged = intent.getIntExtra(BatteryManager.EXTRA_PLUGGED, 0)
            if level < 0 or scale <= 0:
                return "Sir, Android hat keinen gültigen Akkustand geliefert."
            percent = round(level * 100 / scale)
            status_text = {
                2: "Der Akku wird geladen.",
                3: "Der Akku wird derzeit nicht geladen.",
                4: "Der Ladezustand ist unbekannt.",
                5: "Der Akku ist vollständig geladen."
            }.get(status, "Der Ladezustand ist nicht eindeutig.")
            if plugged and status == 3:
                status_text = "Das Gerät ist mit Strom verbunden, lädt laut Android aber gerade nicht."
            return f"Sir, der Akkustand beträgt {percent} Prozent. {status_text}"
        except Exception:
            return ("Sir, ich kann den Akkustand in dieser Pydroid-Umgebung "
                    "nicht auslesen. Die übrigen Offline-Befehle bleiben verfügbar.")

    def open_android_settings(self, setting_type):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Settings = autoclass('android.provider.Settings')
            Intent = autoclass('android.content.Intent')
            actions = {
                "wifi": Settings.ACTION_WIFI_SETTINGS,
                "bluetooth": Settings.ACTION_BLUETOOTH_SETTINGS,
                "settings": Settings.ACTION_SETTINGS
            }
            action = actions[setting_type]
            intent = Intent(action)
            PythonActivity.mActivity.startActivity(intent)
            return {
                "wifi": "Ich öffne die WLAN-Einstellungen, Sir.",
                "bluetooth": "Ich öffne die Bluetooth-Einstellungen, Sir.",
                "settings": "Ich öffne die Android-Einstellungen, Sir."
            }[setting_type]
        except Exception:
            return "Sir, diese Android-Einstellung konnte nicht geöffnet werden."

    def open_phone_app(self, app_type):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            PackageManager = autoclass('android.content.pm.PackageManager')
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()

            if app_type == "dialer":
                intent = Intent(Intent.ACTION_DIAL)
                activity.startActivity(intent)
                return "Ich öffne die Telefon-App, Sir. Es wird kein Anruf gestartet."

            # Try Android's standard app category first.
            category = {
                "clock": "android.intent.category.APP_CLOCK",
                "calendar": "android.intent.category.APP_CALENDAR",
            }[app_type]
            intent = Intent(Intent.ACTION_MAIN)
            intent.addCategory(category)
            if intent.resolveActivity(pm) is not None:
                activity.startActivity(intent)
                return {
                    "clock": "Ich öffne die Uhr-App, Sir.",
                    "calendar": "Ich öffne den Kalender, Sir."
                }[app_type]

            # Fallback: open a suitable installed app through its launcher intent.
            candidates = {
                "clock": [
                    ("com.google.android.deskclock", "com.android.deskclock.DeskClock"),
                    ("com.sec.android.app.clockpackage", "com.sec.android.app.clockpackage.ClockPackage"),
                    ("com.android.deskclock", "com.android.deskclock.DeskClock"),
                ],
                "calendar": [
                    ("com.samsung.android.calendar", "com.android.calendar.AllInOneActivity"),
                    ("com.samsung.android.calendar", "com.samsung.android.app.calendar.activity.MainActivity"),
                    ("com.google.android.calendar", "com.android.calendar.AllInOneActivity"),
                    ("com.android.calendar", "com.android.calendar.AllInOneActivity"),
                ],
            }[app_type]

            # Explicit component intents can work even when Android package
            # visibility prevents querying the installed app by package name.
            for package_name, activity_name in candidates:
                try:
                    explicit = Intent()
                    explicit.setClassName(package_name, activity_name)
                    if explicit.resolveActivity(pm) is not None:
                        activity.startActivity(explicit)
                        return {
                            "clock": "Ich öffne die Uhr-App, Sir.",
                            "calendar": "Ich öffne den Kalender, Sir."
                        }[app_type]
                except Exception:
                    continue

            # Final fallback: ask Android to display the calendar's current time.
            if app_type == "calendar":
                try:
                    Uri = autoclass('android.net.Uri')
                    view_intent = Intent(Intent.ACTION_VIEW)
                    view_intent.setData(Uri.parse("content://com.android.calendar/time/"))
                    activity.startActivity(view_intent)
                    return "Ich versuche, den Kalender zu öffnen, Sir."
                except Exception:
                    pass

            return ("Sir, Android hat den passenden App-Aufruf nicht angenommen. "
                    "Der Kalender ist zwar installiert, aber sein Startaufruf muss "
                    "noch genauer an Ihr Gerät angepasst werden.")
        except Exception:
            return ("Sir, die gewünschte App konnte nicht automatisch geöffnet werden. "
                    "Sie können sie direkt über den Startbildschirm öffnen.")

    def normalize(self, text):
        text = text.lower().strip()
        text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        return re.sub(r"\s+", " ", text)

    def run_command(self):
        raw = self.root.ids.command_input.text.strip()
        command = self.normalize(raw)
        if not command:
            self.set_answer("Bitte geben Sie einen Befehl ein, Sir.")
            return

        # Flexible local phrase matching: many common German formulations map to the same command.
        if any(x in command for x in (
            "akkustand", "akku stand", "batterie", "ladezustand",
            "wie viel akku", "wieviel akku", "wie voll", "akku prozent",
            "wie viel prozent", "wie viele prozent", "laedt mein handy",
            "laedt das handy", "wird mein handy geladen", "wie viel ladung",
            "akku noch", "batterie noch", "restakku"
        )):
            answer = self.get_battery_info()
        elif any(x in command for x in ("wlan einstellungen", "wifi einstellungen",
                                         "oeffne wlan", "oeffne wifi", "wlan anzeigen",
                                         "wlan aufmachen")):
            answer = self.open_android_settings("wifi")
        elif any(x in command for x in ("bluetooth einstellungen", "oeffne bluetooth",
                                         "bluetooth aufmachen")):
            answer = self.open_android_settings("bluetooth")
        elif any(x in command for x in ("android einstellungen", "oeffne einstellungen",
                                         "systemeinstellungen", "handy einstellungen",
                                         "einstellungen aufmachen")):
            answer = self.open_android_settings("settings")
        elif any(x in command for x in ("oeffne uhr", "oeffne die uhr", "uhr starten",
                                         "wecker", "alarm")):
            answer = self.open_phone_app("clock")
        elif any(x in command for x in ("oeffne kalender", "oeffne den kalender",
                                         "kalender starten", "zeige kalender")):
            answer = self.open_phone_app("calendar")
        elif any(x in command for x in ("oeffne telefon", "telefon-app", "waehlen",
                                         "telefon oeffnen", "oeffne waehler", "waehlbildschirm")):
            answer = self.open_phone_app("dialer")
        elif any(x in command for x in ("uhrzeit", "wie spaet", "wie viel uhr",
                                         "wieviel uhr", "aktuelle zeit", "sag mir die zeit")):
            answer = "Sir, es ist " + datetime.now().strftime("%H:%M") + " Uhr."
        elif any(x in command for x in ("datum", "welcher tag", "welches datum",
                                         "heutige datum", "welches datum ist heute",
                                         "sag mir das datum")):
            answer = "Sir, heute ist der " + datetime.now().strftime("%d.%m.%Y") + "."
        elif any(x in command for x in ("wer bist du", "wie heisst du", "dein name")):
            answer = "Ich bin J.A.R.V.I.S., Ihr Offline-Assistent, Sir."
        elif any(x in command for x in ("was kannst du", "hilfe", "befehle", "was geht")):
            answer = self.help_text()
        elif any(x in command for x in ("guten morgen", "hallo", "guten tag", "guten abend")):
            answer = "Guten Tag, Sir. J.A.R.V.I.S. ist einsatzbereit."
        elif any(x in command for x in ("stopp", "stoppe sprache", "ruhe")):
            try:
                if self.tts:
                    self.tts.stop()
            except Exception:
                pass
            answer = "Sprachausgabe gestoppt, Sir."
        elif "gute nacht" in command:
            answer = "Gute Nacht, Sir. Ich bleibe bereit, wenn Sie mich wieder öffnen."
        else:
            answer = ("Diesen Befehl kenne ich noch nicht, Sir. "
                      "Nutzen Sie zunächst die Offline-Befehle oder formulieren Sie ihn anders.")
        self.set_answer(answer)

    def help_text(self):
        return (
            "[b]Offline-Befehle[/b]\n"
            "• Wie spät ist es?\n"
            "• Welches Datum haben wir?\n"
            "• Wie ist mein Akkustand?\n"
            "• Öffne WLAN-Einstellungen\n"
            "• Öffne Bluetooth-Einstellungen\n"
            "• Öffne Android-Einstellungen\n"
            "• Wer bist du?\n"
            "• Was kannst du?\n"
            "• Stopp (Sprachausgabe stoppen)\n\n"
            "Tipp: Sie können das Mikrofon Ihrer Samsung-Tastatur zum Diktieren nutzen; "
            "der erkannte Text erscheint im Befehlsfeld. Danach tippen Sie auf "
            "BEFEHL AUSFÜHREN. Die Diktierfunktion gehört zur Tastatur, nicht zu J.A.R.V.I.S. "
            "Ein eigenes Mikrofon und Aktivierungswort sind noch nicht enthalten."
        )

    def show_help(self):
        self.set_answer(self.help_text())

    def on_stop(self):
        try:
            if self.tts:
                self.tts.stop()
                self.tts.shutdown()
        except Exception:
            pass

if __name__ == "__main__":
    JarvisOfflinePlus().run()