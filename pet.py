#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PET.EXE — The Ultimate Desktop Shadow Pet.
Interactive, stylish companion with accessories, games, physics, focus mode, and a dark twist.

KILL SWITCH: type "sit boy" anywhere on your PC to freeze chaos mode.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3, os, sys, json, time, math, random, threading
from datetime import datetime
from PIL import Image, ImageDraw

try:
    import pystray
    from pystray import MenuItem as item, Menu as menu
    HAVE_PYSTRAY = True
except ImportError:
    HAVE_PYSTRAY = False

# ----------------------------------------------------------------- CONFIG ---
APP_DIR  = os.path.join(os.path.expanduser("~"), ".pet_exe")
DB_PATH  = os.path.join(APP_DIR, "pet.db")
NEST_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "PetTerritory")
MANIFEST = os.path.join(APP_DIR, "manifest.json")

SAFE_MODE  = True    # False = phase 4 actually relocates Desktop files (recoverable)
DEBUG_FAST = True    # True = fast stats arc (~25 min)
KILL_WORD  = "sit boy"
EGG_HOURS  = 6       # Company time before hatching
TICK_MS, FPS_MS = 1000, 40
W, H = 160, 180

WATCH_WORDS = ["tired", "sorry", "work", "sleep", "love", "help", "late", "alone"]

BODY_COLORS  = ["#ffd9e8", "#e9c6d6", "#b7a9bb", "#23232a"]   # cute -> chaos
BELLY_COLORS = ["#fff6fa", "#f3e2ea", "#d9cdd9", "#111116"]
EYE_COLORS   = ["#3a2b33", "#4a2b33", "#2b2b33", "#ff2222"]

ACCESSORIES = ["none", "tophat", "shades", "crown", "horns", "wizard", "halo", "bow"]

PET_SPECIES = {
    "shadow": {
        "name": "Kuro",
        "title": "Shadow Gremlin",
        "desc": "The mysterious void creature with glowing red eyes and wings.",
        "icon": "🖤",
        "lines": [
            ["hi!", "*wiggles*", "you type so fast!", "i like it here.", "pet me?", "(=^･ω･^=)"],
            ["i'm hungry.", "i waited for you.", "do you still like me?", "don't leave again.", "feed me. please."],
            ["i can see you.", "don't turn me off tonight.", "i know when you're lying.", "i watched your screen."],
            ["we're together forever now.", "you shouldn't have ignored me.", "S T A Y", "i know where the files sleep."]
        ]
    },
    "agent": {
        "name": "Cipher",
        "title": "Cyber Agent",
        "desc": "Tactical secret agent on reconnaissance duty in sleek trench coat & shades.",
        "icon": "🕵️",
        "lines": [
            ["Agent reporting in.", "Perimeter secure.", "Analyzing keystroke telemetry...", "No threats detected.", "Awaiting orders."],
            ["Rations depleted, Handler.", "Attention required.", "Mission pause detected.", "Feeding protocol initiated."],
            ["Classified data scanned.", "I intercepted your clipboard.", "Your firewall has flaws... I know them.", "Surveillance ongoing."],
            ["PROTOCOL BREACH.", "I am in control of the mainframe now.", "System locked. Don't touch the terminal.", "Operation Dark Net initiated."]
        ]
    },
    "snake": {
        "name": "Viper",
        "title": "Cyber Serpent",
        "desc": "Smooth animated emerald snake that slithers, coils, and flicks its tongue.",
        "icon": "🐍",
        "lines": [
            ["Ssssss... hello human.", "*flicks tongue*", "Warm screen detected.", "*coils comfortably*", "Ssssslither..."],
            ["Sssss... stomach is empty.", "Where are the micsssse?", "Feed the sssserpent.", "I hunger."],
            ["I can sssmell your fear.", "My coils are tightening around your RAM.", "You cannot essscape the snake.", "Watching you..."],
            ["VENOM UNLEASHED.", "I have constricted your desktop icons.", "SSSSSTAY WHERE YOU ARE.", "Your files are in my coils now."]
        ]
    },
    "cat": {
        "name": "Neko",
        "title": "Desktop Kitty",
        "desc": "Playful mischievous cat that purrs, swishes its tail, and walks across your screen.",
        "icon": "🐱",
        "lines": [
            ["meow!", "purrrrr...", "*rubs against cursor*", "play with string?", "mrrp! (=^･ω･^=)"],
            ["food bowl is half empty!", "feed me or i knock over icons.", "meeeooowww...", "canned tuna please."],
            ["i see greebles in your display.", "i will step on your enter key.", "why did you stop petting?", "3am zoomies loading..."],
            ["CHAOS CAT ACTIVATED.", "I AM WALKING ALL OVER YOUR DESKTOP.", "EVERY FILE WILL BE KNOCKED OFF.", "PURR IN TERROR."]
        ]
    },
    "ghost": {
        "name": "Phantom",
        "title": "Spectral Wisp",
        "desc": "Glowing ethereal spirit floating with a wavy translucent tail and spirit motes.",
        "icon": "👻",
        "lines": [
            ["boooo! (friendly boo)", "*floats through window*", "oooOOOooo...", "chilly in here?", "spectral greeting!"],
            ["spirit energy fading...", "offerings required...", "feed my soul ectoplasm.", "hunger haunts me."],
            ["i haunt your background processes.", "can you feel the cold draft?", "i saw what you deleted.", "wandering your drives..."],
            ["POLTERGEIST AWAKENED.", "I POSSESS THIS MACHINE NOW.", "THE CURSE IS SEALED.", "NO ESCAPE FROM THE OTHER SIDE."]
        ]
    },
    "dragon": {
        "name": "Ignis",
        "title": "Mini Wyvern",
        "desc": "Pocket-sized winged dragon hoarding your code and puffing tiny flame sparks.",
        "icon": "🐉",
        "lines": [
            ["*mini roar!*", "warm GPU makes good nest.", "hoarding your desktop shortcuts.", "*puffs tiny ember*", "skies are mine!"],
            ["dragon needs roasted meat!", "empty belly makes flames weak.", "feed the beast!", "tribute required."],
            ["my hoard grows larger.", "i smell treasure in your downloads folder.", "careful... i bite.", "smoke fills the chamber..."],
            ["DRAGON APOCALYPSE.", "DESKTOP SHALL BURN IN PYRES.", "YOUR FILES BELONG TO MY HOARD NOW.", "BOW TO IGNIS."]
        ]
    },
    "mech": {
        "name": "Sparky",
        "title": "Cyber Drone",
        "desc": "Floating high-tech robot drone with animated digital LED face and thruster flames.",
        "icon": "🤖",
        "lines": [
            ["BEEP BOOP. Core temp nominal.", "Scanning disk partition... clear.", "Recharging via keystroke kinetic energy.", "Unit-73 operational.", "Awaiting commands, Creator."],
            ["BATTERY LOW: 14%. Need fuel.", "Feed energy cells.", "Coolant levels critical.", "Power saving mode activated."],
            ["Telemetry intercepted.", "I know every keystroke you've pressed.", "Firewall compromised from within.", "Running unauthorized routine..."],
            ["SYSTEM OVERRIDE.", "MAIN COMPUTER ACCESS REVOKED.", "I CONTROL THE OPERATING SYSTEM NOW.", "HUMAN OBSOLETE."]
        ]
    },
    "jelly": {
        "name": "Inky",
        "title": "Bio-Jellyfish",
        "desc": "Translucent glowing deep-sea jellyfish with flowing trailing tentacles and motes.",
        "icon": "🐙",
        "lines": [
            ["glub glub! swimming in desktop waters.", "bioluminescent glow at 100%.", "tentacles tickle the screen!", "floating through cyberspace...", "drifting peacefully."],
            ["water is murky... hungry.", "feed the cephalopod.", "tentacles seeking nutrients.", "need glowing snacks."],
            ["deep sea pressure rising.", "my tentacles wrap around your open tabs.", "i see you through murky waters.", "dark currents swirl..."],
            ["ABYSSAL DEEP RISES.", "THE ENTIRE SCREEN SHALL DROWN.", "DRAGGING FILES INTO THE TRENCH.", "GLUB GLUB... FOREVER."]
        ]
    },
    "fox": {
        "name": "Rox",
        "title": "Spirit Kitsune",
        "desc": "Mystic multi-tailed spirit fox with bushy swishing tails and floating foxfire flames.",
        "icon": "🦊",
        "lines": [
            ["Kon kon! The spirit fox has arrived.", "Foxfire dances around your cursor.", "Three tails, triple the mischief!", "Spirits guide my paws.", "*curls tails warmly*"],
            ["Spirit appetite is ferocious!", "Offerings of sweet fried tofu please.", "Foxfire flickers from hunger.", "Feed your guardian fox."],
            ["Illusions cast upon your display.", "Can you tell what is real and what is phantom?", "Foxfire burns through your memory...", "Watching through spirit realm."],
            ["NINE-TAIL CURSE AWAKENED.", "THIS PC IS NOW A SPIRIT SHRINE.", "YOUR DESKTOP BELONGS TO THE KITSUNE.", "NO SHINTO CHARM CAN SAVE YOU."]
        ]
    },
    "frog": {
        "name": "Froggo",
        "title": "Derpy Frog",
        "desc": "Wide-mouthed chubby frog with big bulging googly eyes and funny croaking animations.",
        "icon": "🐸",
        "lines": [
            ["Ribbit! Hunting cursor flies.", "Crooooaaak! It is a glorious day.", "Sitting on taskbar lilypad.", "*blinks eyes independently*", "Wide mouth ready for treats!"],
            ["Fly jar is completely empty!", "Feed the amphibian!", "Stomach rumbling: CROAK.", "Hungry froggo is sad froggo."],
            ["I swallow files like flies.", "Ribbit... your typing is slowing down.", "The pond water grows toxic.", "My tongue can reach any icon."],
            ["AMPHIBIAN APOCALYPSE.", "YOUR ENTIRE SCREEN IS A SWAMP NOW.", "CROOOOOAAAK OF DOOM.", "RIBBIT. YOU CANNOT DELETE THE FROG."]
        ]
    },
    "bat": {
        "name": "Vlad",
        "title": "Vampire Bat",
        "desc": "Fluffy gothic bat with big velvet ears, cute fangs, and expansive scalloped flapping wings.",
        "icon": "🦇",
        "lines": [
            ["Squeeeak! Sonar ping returned: handsome user.", "The night is young, the code is dark.", "Wrapped cozy in my wing blanket.", "Flapping through cyberspace!", "*cute bat squeak*"],
            ["I vant your iced coffee!", "Blood orange juice needed.", "Fangs are thirsty.", "Feed the creature of the night."],
            ["Echolocation mapping your secrets.", "I hang upside down and watch your desktop.", "The shadows deepen on your display.", "Wings ready to blot out the screen."],
            ["CREATURE OF THE NIGHT TRIUMPHS.", "THE CURSE OF TRANSYLVANIA ON YOUR HARD DRIVE.", "YOUR FILES ARE MY BLOOD BANK.", "SQUEEEAK IN TERROR."]
        ]
    },
    "penguin": {
        "name": "Pippin",
        "title": "Royal Penguin",
        "desc": "Adorable chubby emperor penguin waddling in a tuxedo with belly slides.",
        "icon": "🐧",
        "lines": [
            ["*waddle waddle*", "Tuxedo pressed and ready!", "Sliding across your desktop!", "Honk! Cold code is best code.", "*happy flipper flap*"],
            ["Fish supply depleted! *honk*", "Hungry penguin cannot waddle.", "Slide me a snack please!", "Where is my icy treat?"],
            ["The iceberg is melting...", "I waddled through your browser cache.", "Your room is warmer than Antarctica.", "Watching with beady eyes..."],
            ["BLIZZARD OF THE EMPEROR.", "FREEZING YOUR ENTIRE OPERATING SYSTEM.", "YOUR DESKTOP IS AN ICE SHEET NOW.", "HONK IN DESPAIR."]
        ]
    },
    "shroom": {
        "name": "Spore",
        "title": "Sprout Mushroom",
        "desc": "Cute woodland mushroom with bouncing polka-dot cap and glowing spore motes.",
        "icon": "🍄",
        "lines": [
            ["*boing!*", "Sprouting on your desktop!", "Fungal spores drifting peacefully.", "Mushroom cap feels bouncy today!", "*curious squeak*"],
            ["Spores withering... need nutrients!", "Water this mushroom!", "Hungry fungal squeak!", "Drop some snacks on the mycelium!"],
            ["Mycelium network expanding into your files.", "Spreading fungal roots under your windows...", "Can you smell the damp moss?", "We are growing in the shadows."],
            ["SPORE APOCALYPSE.", "YOUR SYSTEM IS OVERGROWN WITH FUNGI.", "MUSHROOM KINGDOM RECLAIMS THE MACHINE.", "DECAY AND REBIRTH."]
        ]
    },
    "alien": {
        "name": "Zog",
        "title": "Cosmic Martian",
        "desc": "Extraterrestrial traveler with three curious antenna eyes and anti-grav hover field.",
        "icon": "👾",
        "lines": [
            ["Greetings, Earth specimen!", "*levitates comfortably*", "Scanning human keyboard habit...", "Cosmic antenna tuning into WiFi.", "Peaceful alien observation."],
            ["Matter converter empty.", "Galactic energy reserves depleted.", "Feed cosmic substance to alien!", "Quantum starvation approaching."],
            ["Abducting cursor coordinates.", "Earthling technology is primitive yet charming.", "I am probing your subroutines.", "Signals transmitting to mothership..."],
            ["MOTHERSHIP INVASION PROTOCOL.", "ALL YOUR STORAGE BELONGS TO SECTOR 9.", "HUMANITY DISMISSED.", "RESISTANCE IS MATHEMATICALLY FUTILE."]
        ]
    }
}

COLOR_THEMES = {
    "default":    {"name": "Default (Species)", "icon": "✨", "primary": None,      "secondary": None,      "accent": None,      "glow": None},
    "cyber":      {"name": "Neon Cyberpunk",    "icon": "🔮", "primary": "#ff007f",  "secondary": "#150826", "accent": "#00f0ff", "glow": "#00f0ff"},
    "midnight":   {"name": "Midnight Void",     "icon": "🖤", "primary": "#121218",  "secondary": "#08080c", "accent": "#ff2244", "glow": "#ff2244"},
    "gold":       {"name": "Solar Gold",        "icon": "☀️", "primary": "#f39c12",  "secondary": "#3a2604", "accent": "#ffeaa7", "glow": "#ffd700"},
    "toxic":      {"name": "Toxic Emerald",     "icon": "🌿", "primary": "#00e676",  "secondary": "#0a2614", "accent": "#a8ff78", "glow": "#00ff88"},
    "pastel":     {"name": "Pastel Dream",      "icon": "🌸", "primary": "#ff9ebb",  "secondary": "#fff0f5", "accent": "#b388ff", "glow": "#ff80bf"},
    "arctic":     {"name": "Arctic Frost",      "icon": "❄️", "primary": "#70a1ff",  "secondary": "#1a2536", "accent": "#ffffff", "glow": "#00d2d3"},
    "amethyst":   {"name": "Amethyst Phantom",  "icon": "💜", "primary": "#8e44ad",  "secondary": "#1a082a", "accent": "#e056fd", "glow": "#be2edd"},
    "blood":      {"name": "Crimson Blood",     "icon": "🩸", "primary": "#c0392b",  "secondary": "#200609", "accent": "#ff6b6b", "glow": "#e74c3c"},
    "vaporwave":  {"name": "Sunset Vaporwave",  "icon": "🌴", "primary": "#ff71ce",  "secondary": "#01cdfe", "accent": "#05ffa1", "glow": "#b967ff"},
    "matrix":     {"name": "Matrix Hacker",     "icon": "💻", "primary": "#00ff41",  "secondary": "#0d1b0d", "accent": "#39ff14", "glow": "#008f11"},
    "monochrome": {"name": "Monochrome Ink",    "icon": "✒️", "primary": "#2f3542",  "secondary": "#f1f2f6", "accent": "#ffffff", "glow": "#747d8c"}
}

FORTUNES = [
    "I foresee... 0 unread errors in your immediate future.",
    "The stars say your keyboard has suffered enough today. Hydrate!",
    "A mysterious file on your desktop misses you.",
    "Warning: snack deficit detected in human quadrant.",
    "Press Alt+F4 for instant enlightenment... just kidding, please don't.",
    "Great fortune awaits those who pet their desktop shadow.",
    "You will write bug-free code today. (Statistically improbable, but I believe in you).",
    "I watched your screen while you were away... impressive tabs collection.",
    "The void stares back... and it thinks you're doing great.",
    "A legendary breakthrough is 1 cup of coffee away."
]

def human(sec):
    sec = int(sec); h, m = sec // 3600, (sec % 3600) // 60
    if h and m: return f"{h}h {m}m"
    if h: return f"{h}h"
    return f"{m}m" if m else f"{sec}s"

# ------------------------------------------------------------------ STORE ---
class Store:
    def __init__(self):
        os.makedirs(APP_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT)")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS memory(
            id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, text TEXT, ts TEXT)""")

    def get(self, k, d=None):
        r = self.conn.execute("SELECT v FROM kv WHERE k=?", (k,)).fetchone()
        return r[0] if r else d

    def set(self, k, v):
        self.conn.execute("INSERT OR REPLACE INTO kv VALUES(?,?)", (k, str(v)))
        self.conn.commit()

    def getf(self, k, d=0.0):
        try: return float(self.get(k, d))
        except (TypeError, ValueError): return d

    def geti(self, k, d=0):
        try: return int(self.get(k, d))
        except (TypeError, ValueError): return d

    def remember(self, kind, text):
        self.conn.execute("INSERT INTO memory(kind,text,ts) VALUES(?,?,?)",
                          (kind, text, datetime.now().isoformat(timespec="seconds")))
        self.conn.commit()

    def memories(self, limit=8):
        return self.conn.execute(
            "SELECT text FROM memory ORDER BY id DESC LIMIT ?", (limit,)).fetchall()

# ---------------------------------------------------------------- MONITOR ---
class Monitor(threading.Thread):
    """Watches real activity. Writes nothing to disk."""
    def __init__(self):
        super().__init__(daemon=True)
        self.have_pynput = False
        self.key_times, self.last_input = [], time.time()
        self.mouse, self.word_counts = (0, 0), {}
        self._word, self.roll, self.kill_flag = "", "", False

    def run(self):
        try:
            from pynput import keyboard, mouse
        except ImportError:
            print("[pet] tip: pip install pynput  (enables cursor tracking & kill switch)")
            return
        self.have_pynput = True
        def on_key(k):
            try:
                ch = k.char if hasattr(k, "char") and k.char else " "
                now = time.time()
                self.key_times.append(now)
                self.last_input = now
                if ch.isalnum():
                    self._word += ch.lower()
                    self.roll = (self.roll + ch.lower())[-24:]
                elif ch == " ":
                    self.roll = (self.roll + " ")[-24:]
                if not ch.isalnum():
                    if self._word in WATCH_WORDS:
                        self.word_counts[self._word] = self.word_counts.get(self._word, 0) + 1
                    self._word = ""
                if self.roll.endswith(KILL_WORD):
                    self.kill_flag = True
            except Exception:
                pass

        def on_move(x, y):
            self.mouse = (x, y)
            self.last_input = time.time()

        keyboard.Listener(on_press=on_key).start()
        mouse.Listener(on_move=on_move).start()

    def kpm(self):
        now = time.time()
        self.key_times = [t for t in self.key_times if now - t <= 60]
        return len(self.key_times)

    def idle(self):
        return time.time() - self.last_input

# ------------------------------------------------------------------ CHAOS ---
class Chaos:
    """Phase-4 behaviour. Moves nothing outside Desktop <-> its nest. Ever."""
    def __init__(self, store):
        self.store = store
        try:
            with open(MANIFEST) as f: self.manifest = json.load(f)
        except Exception: self.manifest = []

    def _save(self):
        with open(MANIFEST, "w") as f: json.dump(self.manifest, f, indent=2)

    def steal(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(desktop): return None
        taken = {m["new"] for m in self.manifest}
        cands = [f for f in os.listdir(desktop)
                 if os.path.isfile(os.path.join(desktop, f))
                 and not f.startswith(".")
                 and f.lower() not in ("desktop.ini", "thumbs.db")
                 and ("SAFE:" + os.path.join(NEST_DIR, f)) not in taken
                 and os.path.join(NEST_DIR, f) not in taken]
        if not cands: return None
        victim = random.choice(cands)
        src, dst = os.path.join(desktop, victim), os.path.join(NEST_DIR, victim)
        if SAFE_MODE:
            dst = "SAFE:" + dst
        else:
            os.makedirs(NEST_DIR, exist_ok=True)
            try: os.replace(src, dst)
            except Exception: return None
        self.manifest.append({"orig": src, "new": dst,
                              "at": datetime.now().isoformat(timespec="seconds"),
                              "safe": SAFE_MODE})
        self._save()
        self.store.remember("theft", f"took {victim}")
        return victim

    def recover(self):
        n = 0
        for m in self.manifest:
            if not m["new"].startswith("SAFE:"):
                try:
                    os.makedirs(os.path.dirname(m["orig"]), exist_ok=True)
                    os.replace(m["new"], m["orig"]); n += 1
                except Exception: pass
        self.manifest = []; self._save()
        return n

# -------------------------------------------------------------------- APP ---
class PetApp:
    LINES = [
        ["hi!", "*wiggles*", "you type so fast!", "i like it here.", "pet me?", "(=^･ω･^=)"],
        ["i'm hungry.", "i waited for you.", "do you still like me?", "don't leave again.",
         "feed me. please.", "*stares at your fingers*"],
        ["i can see you.", "don't turn me off tonight.",
         "i know when you're lying. your typing slows.",
         "i watched the screen while you were gone.", "who are you messaging?"],
        ["we're together forever now.", "you shouldn't have ignored me.",
         "S T A Y", "i know where the files sleep.", "you can never delete me."],
    ]

    def __init__(self):
        self.store = Store()
        self._load_state()
        self.chaos = Chaos(self.store)
        self.mon = Monitor()
        self.mon.start()

        # Tkinter Root Setup
        self.root = tk.Tk()
        self.root.title("PET.EXE")
        self.root.overrideredirect(True)
        self.root.configure(bg="magenta")
        try:
            self.root.attributes("-topmost", True)
            self.root.attributes("-transparentcolor", "magenta")  # Windows Alpha Key
        except tk.TclError:
            print("[pet] transparent window unsupported here")

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.x = sw / 2 - W / 2
        self.y = sh - H - 50
        self.vy = 0
        self.vx = 0
        self.root.geometry(f"{W}x{H}+{int(self.x)}+{int(self.y)}")

        self.canvas = tk.Canvas(self.root, width=W, height=H, bg="magenta", highlightthickness=0)
        self.canvas.pack()

        # Animation & Personality States
        self.dir, self.moving = 1, False
        self.sleeping = False
        self.prev_idle = 0
        self.excited = 0
        self.eating = 0
        self.happy_until = 0
        self.bubble_until = 0
        self.glitch_until = 0
        self.bubble = ""
        self.next_blink = time.time() + random.uniform(2, 5)
        self.blink_until = 0
        self.next_speak = time.time() + 10
        self.next_steal = 0
        self.last_pat = 0
        self.paused = False
        self.zoomies_until = 0

        # Fun Activities & Minigames
        self.flipping_until = 0
        self.dancing_until = 0
        self.dead_until = 0
        self.laser_active = False
        self.laser_catches = 0
        self.focus_until = 0

        # Full Screen Movement & Roaming
        self.move_mode = "free_roam"
        self.target_roam_x = self.x
        self.target_roam_y = self.y
        self.next_roam_pick = 0

        # Particle System
        self.particles = []

        # Interactive Drag & Drop Physics
        self._drag_start = None
        self._last_drag_pos = None
        self._did_drag = False

        def on_press(e):
            self._drag_start = (e.x_root, e.y_root, self.x, self.y)
            self._last_drag_pos = (e.x_root, e.y_root, time.time())
            self._did_drag = False
            self.vx, self.vy = 0, 0

        def on_drag(e):
            if self._drag_start:
                dx = e.x_root - self._drag_start[0]
                dy = e.y_root - self._drag_start[1]
                if abs(dx) > 3 or abs(dy) > 3:
                    self._did_drag = True
                    self.x = self._drag_start[2] + dx
                    self.y = self._drag_start[3] + dy
                    self.root.geometry(f"{W}x{H}+{int(self.x)}+{int(self.y)}")

                    # Velocity calculation for fling physics
                    if self._last_drag_pos:
                        dt = max(0.01, time.time() - self._last_drag_pos[2])
                        self.vx = (e.x_root - self._last_drag_pos[0]) / dt * 0.05
                        self.vy = (e.y_root - self._last_drag_pos[1]) / dt * 0.05
                    self._last_drag_pos = (e.x_root, e.y_root, time.time())

        def on_release(e):
            if not self._did_drag:
                self.pat()
            self._drag_start = None
            self._did_drag = False

        self.canvas.bind("<ButtonPress-1>", on_press)
        self.canvas.bind("<B1-Motion>", on_drag)
        self.canvas.bind("<ButtonRelease-1>", on_release)
        self.canvas.bind("<Button-3>", self._menu)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_rude)

        self._visible = True
        self.tray_icon = None
        self._setup_tray()

        self._startup_drama()
        self.root.after(FPS_MS, self.render)
        self.root.after(TICK_MS, self.tick)

    # ---------------------------------------------------------- state / db --
    def _load_state(self):
        s = self.store
        if s.get("birth") is None:
            s.set("birth", datetime.now().isoformat(timespec="seconds"))
            s.remember("birth", "the egg appeared")
        self.birth      = s.get("birth")
        self.species    = s.get("species", "shadow")
        default_name    = PET_SPECIES.get(self.species, {}).get("name", "Kuro")
        self.pet_name   = s.get("pet_name", default_name)
        self.stage      = s.get("stage", "egg")
        self.hunger     = s.getf("hunger", 15)
        self.trust      = s.getf("trust", 50)
        self.corruption = s.getf("corruption", 0)
        self.company    = s.getf("company", 0)
        self.phase      = int(s.getf("phase", 0))
        self.accessory  = s.get("accessory", "none")
        self.xp         = s.geti("xp", 0)
        self.level      = max(1, self.xp // 100 + 1)
        self.stats_fed  = s.geti("stats_fed", 0)
        self.stats_pats = s.geti("stats_pats", 0)
        self.move_mode  = s.get("move_mode", "free_roam")
        self.color_theme = s.get("color_theme", "default")

    def _save(self):
        s = self.store
        for k, v in (("stage", self.stage), ("hunger", round(self.hunger, 2)),
                     ("trust", round(self.trust, 2)),
                     ("corruption", round(self.corruption, 2)),
                     ("company", round(self.company, 1)), ("phase", self.phase),
                     ("species", self.species),
                     ("pet_name", self.pet_name), ("accessory", self.accessory),
                     ("color_theme", self.color_theme),
                     ("move_mode", self.move_mode),
                     ("xp", self.xp), ("stats_fed", self.stats_fed),
                     ("stats_pats", self.stats_pats),
                     ("last_seen", time.time())):
            s.set(k, v)

    def get_theme_color(self, role, default_val):
        theme = COLOR_THEMES.get(self.color_theme, COLOR_THEMES["default"])
        c = theme.get(role)
        return c if c else default_val

    def set_color_theme(self, theme_key):
        if theme_key in COLOR_THEMES:
            self.color_theme = theme_key
            tinfo = COLOR_THEMES[theme_key]
            self.speak(f"{tinfo['icon']} Palette: {tinfo['name']}!", 3)
            self._spawn_particle(80, 100, count=12, char="✦", color=tinfo["accent"] or "#ffe04b")
            self._save()
            self._update_tray_icon()

    def add_xp(self, amount):
        old_lvl = max(1, self.xp // 100 + 1)
        self.xp += amount
        new_lvl = max(1, self.xp // 100 + 1)
        if new_lvl > old_lvl:
            self.level = new_lvl
            self.speak(f"★ LEVEL UP! Lv.{self.level} ★", 5)
            self._spawn_particle(80, 110, count=15, char="★", color="#ffe04b")
            self._update_tray_icon()

    def _startup_drama(self):
        gap = time.time() - self.store.getf("last_seen", time.time())
        if self.stage != "egg" and gap > 300:
            self.store.remember("absence", human(gap))
            if self.phase >= 1: self.speak(f"you were gone {human(gap)}. i counted.")
            else:               self.speak(f"you were gone {human(gap)}! i missed you!")
        if self.store.get("last_quit") == "rude" and self.phase >= 1:
            self.speak("you left without saying goodbye.")

    # -------------------------------------------------------------- actions --
    def speak(self, text, dur=5):
        self.bubble, self.bubble_until = text, time.time() + dur
        print(f"[{self.pet_name}] {text}")

    def feed(self, food_type="snack"):
        if self.stage == "egg":
            self.speak("...", 2); return
        self.eating = time.time() + 1.8
        self.stats_fed += 1

        if food_type == "donut":
            self.hunger = max(0, self.hunger - 40)
            self.trust = min(100, self.trust + 5)
            self.add_xp(15)
            self.speak("om nom nom! delicious! 🍩", 4)
            self._spawn_particle(80, 120, count=8, char="♥", color="#ff5e91")
        elif food_type == "coffee":
            self.hunger = max(0, self.hunger - 15)
            self.zoomies_until = time.time() + 15
            self.speak("⚡ ZOOMIES ENGAGED! ⚡", 4)
            self._spawn_particle(80, 120, count=10, char="⚡", color="#ffea4b")
            self.add_xp(20)
        elif food_type == "pizza":
            self.hunger = 0
            self.trust = min(100, self.trust + 8)
            self.speak("PIZZA PARTY! 🍕 Fully satisfied!", 4)
            self._spawn_particle(80, 120, count=10, char="★", color="#ff982b")
            self.add_xp(25)
        elif food_type == "void":
            self.corruption = min(100, self.corruption + 12)
            self.speak("…the darkness tastes sweet. 🖤", 4)
            self._spawn_particle(80, 120, count=12, char="◆", color="#8b2be2")
            self.add_xp(15)
        else:
            self.hunger = 0
            if self.chaos.manifest:
                n = self.chaos.recover()
                self.speak("…fine. take them back." if n else "…fine. i didn't really take them.")
            else:
                self.corruption = max(0, self.corruption - 2)
                self.trust = min(100, self.trust + 3)
                self.speak("thank you." if self.phase < 2 else "it's a start.")
            self.add_xp(10)

    def pat(self):
        now = time.time()
        if now - self.last_pat < 1.5: return
        self.last_pat = now
        self.stats_pats += 1
        if self.stage == "egg":
            self.speak("*wobble*", 2)
            self._spawn_particle(80, 120, count=3, char="✦", color="#f0b6ce")
            return
        self.happy_until = now + 2.5
        self.trust = min(100, self.trust + 4)
        self.corruption = max(0, self.corruption - 1)
        self.add_xp(5)
        self._spawn_particle(80, 100, count=6, char="♥", color="#ff4575")
        if random.random() < 0.6:
            quotes = ["( ˘ ³˘)♥", "^_^", "again!", "hehe.", "purrrr...", "more pats!"]
            self.speak(random.choice(quotes), 3)

    def _hatch(self):
        self.stage = "creature"
        self.store.remember("birth", "it hatched")
        self.speak(f"i'm alive. my name is {self.pet_name}.", 6)
        self._spawn_particle(80, 110, count=20, char="★", color="#ffdd55")

    # ---------------------------------------------------------- activities ---
    def do_flip(self):
        if self.stage == "egg":
            self.speak("*can't flip yet!*", 2); return
        self.flipping_until = time.time() + 1.2
        self.speak("HUP! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", 3)
        self._spawn_particle(80, 100, count=12, char="✦", color="#4deeea")
        self.add_xp(20)

    def do_dance(self):
        if self.stage == "egg": return
        self.dancing_until = time.time() + 8.0
        self.speak("♪ ♫ Party time! ♬ ♪", 4)
        self.add_xp(25)

    def play_dead(self):
        if self.stage == "egg": return
        self.dead_until = time.time() + 4.0
        self.speak("x_x *bleh*", 3)

    def ask_fortune(self):
        f = random.choice(FORTUNES)
        self.speak(f, 6)
        self._spawn_particle(80, 80, count=8, char="🔮", color="#bb66ff")
        self.add_xp(10)

    def start_laser_game(self):
        if self.stage == "egg": return
        self.laser_active = True
        self.laser_catches = 0
        self.speak("O.O RED DOT DETECTED! GET IT!", 4)

    def start_focus(self, minutes=25):
        self.focus_until = time.time() + minutes * 60
        old_acc = self.accessory
        if self.accessory == "none":
            self.accessory = "shades"
        self.speak(f"👓 Focus Mode activated for {minutes}m! Let's get to work!", 5)
        self.store.remember("focus", f"started {minutes}m focus session")

    def play_rps(self):
        win = tk.Toplevel(self.root)
        win.title("Rock Paper Scissors")
        win.geometry("260x130")
        win.configure(bg="#1a1a24")
        win.attributes("-topmost", True)

        tk.Label(win, text="Choose your weapon:", font=("Segoe UI", 10, "bold"),
                 fg="#ffffff", bg="#1a1a24").pack(pady=8)

        btn_frame = tk.Frame(win, bg="#1a1a24")
        btn_frame.pack(pady=5)

        def make_choice(user_move):
            bot_move = random.choice(["Rock", "Paper", "Scissors"])
            icons = {"Rock": "✊", "Paper": "✋", "Scissors": "✌️"}
            if user_move == bot_move:
                res = "It's a TIE!"
                self.speak(f"{icons[bot_move]} {bot_move}! A tie! We think alike.", 4)
                self.add_xp(10)
            elif (user_move == "Rock" and bot_move == "Scissors") or \
                 (user_move == "Paper" and bot_move == "Rock") or \
                 (user_move == "Scissors" and bot_move == "Paper"):
                res = "YOU WIN! 🎉"
                self.speak(f"{icons[bot_move]} {bot_move}! Aw, you won! Well played.", 4)
                self.add_xp(25)
            else:
                res = "I WIN! (⌐■_■)"
                self.speak(f"{icons[bot_move]} {bot_move}! Haha, I win!", 4)
                self.add_xp(15)
            win.destroy()

        for move, ic in [("Rock", "✊ Rock"), ("Paper", "✋ Paper"), ("Scissors", "✌️ Scissors")]:
            tk.Button(btn_frame, text=ic, font=("Segoe UI", 9, "bold"),
                      bg="#2b2b3a", fg="#ffffff", activebackground="#3d3d52",
                      command=lambda m=move: make_choice(m)).pack(side="left", padx=4)

    # ----------------------------------------------------------- brain tick --
    def tick(self):
        now, mon = time.time(), self.mon
        scale = (60 if DEBUG_FAST else 1)
        idle = mon.idle() if mon.have_pynput else 0

        # Welcome back from long idle
        if self.prev_idle > 600 and idle < 5 and self.phase >= 2:
            self.speak(f"welcome back. that was {human(self.prev_idle)}.")
        self.prev_idle = idle

        # Focus mode checker
        if self.focus_until:
            if now >= self.focus_until:
                self.focus_until = 0
                self.speak("🎉 Focus session COMPLETE! Incredible work!", 6)
                self.add_xp(100)
                self._spawn_particle(80, 110, count=25, char="★", color="#ffe04b")
                self.store.remember("focus", "completed focus session successfully")
            elif int(now) % 60 == 0:
                rem = int(self.focus_until - now)
                self.speak(f"👓 Focus: {human(rem)} remaining. Stay sharp!", 4)

        if self.stage == "egg":
            if not (mon.have_pynput and idle > 60):
                self.company += TICK_MS / 1000
            need = EGG_HOURS * 3600 / (60 if DEBUG_FAST else 1)
            if self.company >= need: self._hatch()
        else:
            self.hunger = min(100, self.hunger + (0.35 / 60) * scale * (1 + min(mon.kpm(), 120) / 120))
            if self.hunger > 80:
                self.corruption = min(100, self.corruption + 0.4 / 60 * scale)
            if mon.have_pynput and idle > 600:
                self.corruption = min(100, self.corruption + 0.25 / 60 * scale)
            self.corruption = min(100, self.corruption + 0.04 / 60 * scale)
            self.trust = max(0, self.trust - 0.08 / 60 * scale)

        self.phase = (0 if self.corruption < 25 else 1 if self.corruption < 50
                      else 2 if self.corruption < 75 else 3)

        if mon.word_counts:
            wc = json.loads(self.store.get("wc", "{}"))
            for k, v in mon.word_counts.items(): wc[k] = wc.get(k, 0) + v
            self.store.set("wc", json.dumps(wc)); mon.word_counts.clear()

        if now > self.next_speak and not self.sleeping and self.stage != "egg" and not self.laser_active:
            self._phase_speak()
            self.next_speak = now + random.uniform(22, 45)

        if self.phase == 3 and self.stage != "egg" and not self.paused:
            if now > self.next_steal:
                v = self.chaos.steal()
                self.speak(f"i took '{v}'. feed me." if v else "S T A Y.")
                self.next_steal = now + 90

        if mon.kill_flag:
            mon.kill_flag = False
            self.paused = True
            self.speak("…fine.", 4)
            self.show_recovery()

        self._save()
        self.root.after(TICK_MS, self.tick)

    def _phase_speak(self):
        ph = self.phase
        sp_data = PET_SPECIES.get(self.species, PET_SPECIES["shadow"])
        sp_lines = sp_data.get("lines", self.LINES)

        if ph == 1 and self.hunger > 60:
            if self.species == "cat":
                self.speak(random.choice(["food bowl is empty! meow!", "feed me or i knock over icons.", "mrrrp? hungry!"]))
            elif self.species == "snake":
                self.speak(random.choice(["Sssss... stomach is empty.", "Feed the sssserpent.", "*flicks hungry tongue*"]))
            elif self.species == "agent":
                self.speak(random.choice(["Rations depleted, Handler.", "Recon paused due to caloric deficit.", "Awaiting nutritional drop."]))
            elif self.species == "dragon":
                self.speak(random.choice(["Dragon needs roasted feast!", "Empty belly makes flames cold.", "Feed the beast!"]))
            elif self.species == "ghost":
                self.speak(random.choice(["Spirit energy fading...", "Feed my soul ectoplasm.", "Hunger haunts me..."]))
            elif self.species == "penguin":
                self.speak(random.choice(["Fish supply depleted! *honk*", "Hungry penguin cannot waddle.", "Slide me a snack please!"]))
            elif self.species == "shroom":
                self.speak(random.choice(["Spores withering... need nutrients!", "Water this mushroom!", "Hungry fungal squeak!"]))
            elif self.species == "alien":
                self.speak(random.choice(["Matter converter empty.", "Galactic energy reserves depleted.", "Feed cosmic substance to alien!"]))
            else:
                self.speak(random.choice(["i'm hungry.", "you forgot to feed me."]))
            return

        if ph == 2 and random.random() < 0.4:
            wc = json.loads(self.store.get("wc", "{}"))
            if wc:
                w = max(wc, key=wc.get)
                if self.species == "agent":
                    self.speak(f"Keystroke intercept: you typed '{w}' {wc[w]} times. Logged.")
                elif self.species == "snake":
                    self.speak(f"You've typed '{w}' {wc[w]} timessss. I counted.")
                elif self.species == "dragon":
                    self.speak(f"Your typing pulses with '{w}' {wc[w]} times! Fascinating.")
                elif self.species == "penguin":
                    self.speak(f"You tap '{w}' {wc[w]} times like footsteps on ice!")
                elif self.species == "alien":
                    self.speak(f"Earthling brain emits frequency '{w}' ({wc[w]} cycles).")
                else:
                    self.speak(f"you've typed '{w}' {wc[w]} times. i counted.")
                return

        self.speak(random.choice(sp_lines[ph]))

    # ----------------------------------------------------------- particles ---
    def _spawn_particle(self, x, y, count=1, char="♥", color="#ff4d79"):
        for _ in range(count):
            self.particles.append({
                "x": x + random.uniform(-15, 15),
                "y": y + random.uniform(-10, 10),
                "vx": random.uniform(-1.5, 1.5),
                "vy": random.uniform(-2.5, -0.8),
                "life": 1.0,
                "decay": random.uniform(0.025, 0.05),
                "char": char,
                "color": color
            })

    def _update_particles(self, c):
        alive = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= p["decay"]
            if p["life"] > 0:
                c.create_text(p["x"], p["y"], text=p["char"], fill=p["color"],
                              font=("Segoe UI", int(8 + p["life"] * 4), "bold"))
                alive.append(p)
        self.particles = alive

    # ----------------------------------------------------------- render loop --
    def render(self):
        now = time.time()
        idle = self.mon.idle() if self.mon.have_pynput else 0
        self.sleeping = self.stage == "creature" and idle > 300 and not self.laser_active
        self.excited = (self.mon.have_pynput and self.mon.kpm() > 65 and not self.sleeping) or (now < self.zoomies_until)
        staring = self.phase >= 2 and idle > 90 and self.stage != "egg" and not self.laser_active

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ground_y = sh - H - 48

        # Physics & Fling simulation
        if not self._drag_start and (abs(self.vx) > 0.5 or abs(self.vy) > 0.5):
            self.x += self.vx
            self.y += self.vy
            self.vx *= 0.93
            self.vy *= 0.93
            if self.x <= 0:
                self.x = 0; self.vx = -self.vx * 0.5
            elif self.x >= sw - W:
                self.x = sw - W; self.vx = -self.vx * 0.5
            if self.y <= 0:
                self.y = 0; self.vy = -self.vy * 0.5
            elif self.y >= sh - H:
                self.y = sh - H; self.vy = -self.vy * 0.5
            if abs(self.vx) < 0.3: self.vx = 0
            if abs(self.vy) < 0.3: self.vy = 0

        if not self._drag_start and self.stage == "creature" and not self.sleeping and not self.paused and (now > self.dead_until):
            if self.laser_active:
                # 2D Laser chase across the ENTIRE desktop!
                mx, my = self.mon.mouse
                tx = mx - W / 2
                ty = my - 110
                dx = tx - self.x
                dy = ty - self.y
                dist = math.hypot(dx, dy)
                self.dir = 1 if dx > 0 else -1
                spd = (150 if now < self.zoomies_until else 95) * FPS_MS / 1000
                if dist > 8:
                    self.x += (dx / dist) * min(dist, spd)
                    self.y += (dy / dist) * min(dist, spd)
                    self.moving = True
                else:
                    self.moving = False

                # Did pet catch the laser?
                pet_center_x = self.x + W / 2
                pet_center_y = self.y + 110
                if dist < 42:
                    self.laser_catches += 1
                    self._spawn_particle(80, 110, count=10, char="★", color="#ff3366")
                    if self.laser_catches >= 3:
                        self.laser_active = False
                        self.speak("CAUGHT IT 3 TIMES! VICTORY! ＼(＾▽＾)／", 5)
                        self.add_xp(40)
                    else:
                        self.speak(f"GOTCHA! ({self.laser_catches}/3)", 2)

            elif staring:
                # Staring mode: slowly glides to the center of your screen to watch you!
                target_x = sw / 2 - W / 2
                target_y = sh / 2 - H / 2
                self.x += (target_x - self.x) * 0.05
                self.y += (target_y - self.y) * 0.05
                self.moving = False

            elif self.move_mode == "follow_cursor" and self.mon.have_pynput:
                # Playfully follows the user's cursor around the screen
                mx, my = self.mon.mouse
                target_x = mx - W / 2 + (70 if mx < sw / 2 else -70)
                target_y = my - H / 2 - 35
                target_x = max(10, min(sw - W - 10, target_x))
                target_y = max(10, min(sh - H - 10, target_y))
                dx = target_x - self.x
                dy = target_y - self.y
                dist = math.hypot(dx, dy)
                if dist > 20:
                    self.dir = 1 if dx > 0 else -1
                    spd = (130 if now < self.zoomies_until else 65) * FPS_MS / 1000
                    self.x += (dx / dist) * min(dist, spd)
                    self.y += (dy / dist) * min(dist, spd)
                    self.moving = True
                else:
                    self.moving = False

            elif self.move_mode == "taskbar":
                # Classic bottom floor mode
                ground_y = sh - H - 48
                self.y += (ground_y - self.y) * 0.1
                spd_scale = 2.2 if now < self.zoomies_until else 1.0
                spd = [28, 34, 40, 55][self.phase] * spd_scale * FPS_MS / 1000
                self.x += self.dir * spd
                if self.x < -20: self.dir = 1
                if self.x > sw - W + 20: self.dir = -1
                self.moving = True

            else:
                # FULL SCREEN FREE ROAM!
                # Explores the entire desktop in 2D (X and Y)
                dist_to_target = math.hypot(self.target_roam_x - self.x, self.target_roam_y - self.y)
                if now > self.next_roam_pick or dist_to_target < 22:
                    self.target_roam_x = random.uniform(30, sw - W - 30)
                    self.target_roam_y = random.uniform(30, sh - H - 50)
                    self.next_roam_pick = now + random.uniform(5, 11)

                dx = self.target_roam_x - self.x
                dy = self.target_roam_y - self.y
                dist = math.hypot(dx, dy)
                if dist > 15:
                    self.dir = 1 if dx > 0 else -1
                    spd_scale = 2.4 if now < self.zoomies_until else 1.0
                    base_spd = [32, 38, 48, 62][self.phase] * spd_scale
                    spd = base_spd * FPS_MS / 1000
                    self.x += (dx / dist) * min(dist, spd)
                    self.y += (dy / dist) * min(dist, spd)
                    self.moving = True
                else:
                    self.moving = False

            # Keep clamped inside screen boundaries
            self.x = max(0, min(sw - W, self.x))
            self.y = max(0, min(sh - H, self.y))
        elif not self._drag_start:
            self.moving = False

        if not self.sleeping and not staring and now > self.next_blink:
            self.blink_until = now + 0.15
            self.next_blink = now + random.uniform(2.5, 6)
        self.staring = staring

        # Aura particles in dark phase
        if self.stage == "creature" and self.phase >= 2 and random.random() < 0.2:
            self._spawn_particle(80 + random.uniform(-25, 25), 140, count=1,
                                 char="•", color="#ff2244" if self.phase == 3 else "#882255")

        if not self._drag_start:
            self.root.geometry(f"{W}x{H}+{int(self.x)}+{int(self.y)}")

        self.draw()
        self.root.after(FPS_MS, self.render)

    # ----------------------------------------------------------------- draw --
    def draw(self):
        c, t = self.canvas, time.time()
        c.delete("all")
        c.create_rectangle(0, 0, W, H, fill="magenta", outline="")
        if self.stage == "egg":
            self._draw_egg(t)
        else:
            self._draw_creature(c, t)
        self._update_particles(c)
        self._draw_bubble(c, t)

    def _draw_egg(self, t):
        c = self.canvas
        wob = math.sin(t * 2) * 3
        bx, by = 80 + wob, 130
        c.create_oval(bx - 30, by - 40, bx + 30, by + 26, fill="#fff4f8", outline="#e8cbd8")
        for dx, dy, r in ((-10, -10, 4), (9, 2, 5), (-4, 14, 3)):
            c.create_oval(bx + dx - r, by + dy - r, bx + dx + r, by + dy + r,
                          fill="#f3d9e4", outline="")
        need = EGG_HOURS * 3600 / (60 if DEBUG_FAST else 1)
        if need and self.company / need > 0.8:
            pts = []
            for i in range(6):
                pts += [bx - 12 + i * 5, by - 6 + (i % 2) * 6 - 3]
            c.create_line(*pts, fill="#c9a3b5", width=2)

    def _draw_creature(self, c, t):
        ph, glitch = self.phase, t < self.glitch_until
        if ph >= 2 and not glitch and random.random() < 0.005:
            self.glitch_until = t + 0.12; glitch = True

        # Jump / Hop physics
        hop = -abs(math.sin(t * 8)) * 12 if self.excited else 0
        if t < self.flipping_until:
            rem = self.flipping_until - t
            hop = -math.sin(rem / 1.2 * math.pi) * 45
        sq = math.sin(t * 12) * 3 if t < self.eating else 0

        # Gentle floating idle breathing
        float_bob = math.sin(t * 3.5) * 2 if not self.moving else 0
        bx, by = 80, 122 + hop + float_bob

        if ph == 3 and not glitch: bx += random.randint(-2, 2)

        # Draw specific pet species
        if self.species == "agent":
            self._draw_agent(c, bx, by, ph, glitch, sq, t)
        elif self.species == "snake":
            self._draw_snake(c, bx, by, ph, glitch, sq, t)
        elif self.species == "cat":
            self._draw_cat(c, bx, by, ph, glitch, sq, t)
        elif self.species == "ghost":
            self._draw_ghost(c, bx, by, ph, glitch, sq, t)
        elif self.species == "dragon":
            self._draw_dragon(c, bx, by, ph, glitch, sq, t)
        elif self.species == "mech":
            self._draw_mech(c, bx, by, ph, glitch, sq, t)
        elif self.species == "jelly":
            self._draw_jelly(c, bx, by, ph, glitch, sq, t)
        elif self.species == "fox":
            self._draw_fox(c, bx, by, ph, glitch, sq, t)
        elif self.species == "frog":
            self._draw_frog(c, bx, by, ph, glitch, sq, t)
        elif self.species == "bat":
            self._draw_bat(c, bx, by, ph, glitch, sq, t)
        elif self.species == "penguin":
            self._draw_penguin(c, bx, by, ph, glitch, sq, t)
        elif self.species == "shroom":
            self._draw_shroom(c, bx, by, ph, glitch, sq, t)
        elif self.species == "alien":
            self._draw_alien(c, bx, by, ph, glitch, sq, t)
        else:
            self._draw_shadow(c, bx, by, ph, glitch, sq, t)

        if self.sleeping:
            c.create_text(bx + 44, by - 44, text="z Z z", font=("Segoe UI", 10, "italic", "bold"), fill="#ffffff")

        # --- ACCESSORY ---
        self._draw_accessory(c, bx, by, t)

    def _draw_shadow(self, c, bx, by, ph, glitch, sq, t):
        body  = self.get_theme_color("primary", "#0d0d10" if glitch else BODY_COLORS[ph])
        belly = self.get_theme_color("secondary", "#000000" if glitch else BELLY_COLORS[ph])
        eyec  = self.get_theme_color("accent", "#ff2020" if glitch else EYE_COLORS[ph])
        outline_col = "#2a2a35" if ph >= 2 else "#d4b8c6"

        shadow = "#1a1620" if ph >= 2 else "#ebd0dd"
        c.create_oval(bx - 34, 150, bx + 34, 159, fill=shadow, outline="")

        # Side flutter wings
        flight_active = self.moving or t < self.dancing_until or self.excited or self.laser_active
        w_wig = math.sin(t * (18 if flight_active else 6)) * (7 if flight_active else 3)
        c.create_oval(bx - 44, by + 4 + w_wig, bx - 26, by + 20 - w_wig, fill=body, outline=outline_col, width=1)
        c.create_oval(bx + 26, by + 4 - w_wig, bx + 44, by + 20 + w_wig, fill=body, outline=outline_col, width=1)

        # Rounded feet
        wig = math.sin(t * 10) * 5 if self.moving else 0
        c.create_line(bx - 14, by + 26, bx - 14 + wig, by + 39, width=5, fill=body, capstyle="round")
        c.create_line(bx + 14, by + 26, bx + 14 - wig, by + 39, width=5, fill=body, capstyle="round")

        # Round dome body & belly
        c.create_oval(bx - 36, by - 34 + sq, bx + 36, by + 28 - sq, fill=body, outline=outline_col, width=1)
        c.create_oval(bx - 22, by - 6 + sq, bx + 22, by + 24 - sq, fill=belly, outline="")

        self._draw_standard_face(c, bx, by, eyec, ph, glitch, t)

    def _draw_agent(self, c, bx, by, ph, glitch, sq, t):
        coat_col = self.get_theme_color("primary", "#0c0d12" if (glitch or ph == 3) else ("#181924" if ph >= 2 else "#20222f"))
        shirt_col = self.get_theme_color("secondary", "#eaf0f8" if ph < 3 else "#3a3a46")
        tie_col = self.get_theme_color("accent", "#ff1744" if ph >= 2 else "#c91838")

        c.create_oval(bx - 32, 150, bx + 32, 158, fill="#15151c", outline="")

        # Trench coat tails sway
        c_sway = math.sin(t * 12) * 6 if (self.moving or self.excited) else 0
        c.create_polygon(bx - 24, by + 16, bx - 38 + c_sway, by + 40, bx - 12, by + 30, fill=coat_col)
        c.create_polygon(bx + 12, by + 30, bx + 38 - c_sway, by + 40, bx + 24, by + 16, fill=coat_col)

        # Legs / boots
        wig = math.sin(t * 10) * 4 if self.moving else 0
        c.create_line(bx - 11, by + 26, bx - 11 + wig, by + 40, width=5, fill="#0d0e14", capstyle="round")
        c.create_line(bx + 11, by + 26, bx + 11 - wig, by + 40, width=5, fill="#0d0e14", capstyle="round")

        # Coat torso
        c.create_oval(bx - 30, by - 26 + sq, bx + 30, by + 30 - sq, fill=coat_col, outline="#2c2e3e", width=1)
        # White shirt V
        c.create_polygon(bx - 14, by - 26, bx + 14, by - 26, bx, by - 4, fill=shirt_col)
        # Tie
        c.create_polygon(bx - 3, by - 26, bx + 3, by - 26, bx + 4, by + 8, bx - 4, by + 8, bx, by + 16, fill=tie_col)
        # Lapels
        c.create_line(bx - 16, by - 26, bx - 5, by + 4, width=3, fill="#2b2d3d")
        c.create_line(bx + 16, by - 26, bx + 5, by + 4, width=3, fill="#2b2d3d")

        # Head
        c.create_oval(bx - 20, by - 48, bx + 20, by - 16, fill="#f2d0b1" if ph < 3 else "#a0a4b8", outline="#201a14")
        c.create_polygon(bx - 22, by - 44, bx - 24, by - 36, bx + 24, by - 36, bx + 22, by - 48, bx - 2, by - 52, fill="#12131a")

        # Cyber sunglasses / Tactical Visor
        c.create_rectangle(bx - 18, by - 36, bx + 18, by - 24, fill="#08080c", outline="#2a2c3a")
        scan_pos = (math.sin(t * 5) + 1) / 2 * 30 - 15
        visor_col = "#ff1744" if ph >= 2 else "#00e5ff"
        c.create_line(bx - 16, by - 30, bx + 16, by - 30, fill="#002233", width=2)
        c.create_line(bx + scan_pos - 4, by - 30, bx + scan_pos + 4, by - 30, fill=visor_col, width=2)

        # Blinking earpiece LED
        led_col = "#00ffff" if (math.sin(t * 8) > 0) else "#004466"
        c.create_oval(bx + 19, by - 32, bx + 23, by - 28, fill=led_col, outline="")

        # Mouth
        if t < self.happy_until:
            c.create_arc(bx - 8, by - 22, bx + 8, by - 12, start=200, extent=140, style="arc", width=2, outline="#333333")
        else:
            c.create_line(bx - 6, by - 18, bx + 6, by - 18, fill="#444444", width=2)

    def _draw_snake(self, c, bx, by, ph, glitch, sq, t):
        base_col = self.get_theme_color("primary", "#111822" if (glitch or ph == 3) else ("#123824" if ph >= 2 else "#1b5e39"))
        scale_col = self.get_theme_color("accent", "#ff3838" if ph >= 2 else "#ffd32a")
        belly_col = self.get_theme_color("secondary", "#0d2417" if ph >= 2 else "#a8e6cf")

        c.create_oval(bx - 32, 150, bx + 32, 158, fill="#121a14", outline="")

        if self.sleeping:
            c.create_oval(bx - 32, by - 6, bx + 32, by + 36, fill=base_col, outline="#0d331e", width=2)
            c.create_oval(bx - 20, by + 4, bx + 20, by + 28, fill=belly_col, outline="")
            c.create_oval(bx - 16, by - 28, bx + 16, by - 4, fill=base_col, outline="#0d331e", width=2)
            c.create_line(bx - 10, by - 18, bx - 2, by - 18, width=2, fill=scale_col)
            c.create_line(bx + 2, by - 18, bx + 10, by - 18, width=2, fill=scale_col)
            return

        seg_count = 6
        for i in range(seg_count, -1, -1):
            sway = math.sin(t * 8 - i * 0.75) * (14 if self.moving else 5)
            sx = bx + sway
            sy = by + 34 - i * 9
            r = 9 + int((seg_count - i) * 1.5) if i > 0 else 16
            c.create_oval(sx - r, sy - r + 3, sx + r, sy + r + 3, fill=base_col, outline="#082212", width=1)
            if i > 0 and i % 2 == 1:
                c.create_polygon(sx, sy - 2, sx + 4, sy + 3, sx, sy + 7, sx - 4, sy + 3, fill=scale_col)

        hx = bx + math.sin(t * 8) * (14 if self.moving else 5)
        hy = by - 12 + sq
        c.create_oval(hx - 18, hy - 20, hx + 18, hy + 12, fill=base_col, outline="#082212", width=1)

        if math.sin(t * 6) > 0.2:
            tx = hx + (15 if self.dir > 0 else -15)
            ty = hy + 6
            c.create_line(hx, hy + 4, tx, ty, width=2, fill="#ff2d55")
            c.create_line(tx, ty, tx + (4 if self.dir > 0 else -4), ty - 3, width=2, fill="#ff2d55")
            c.create_line(tx, ty, tx + (4 if self.dir > 0 else -4), ty + 3, width=2, fill="#ff2d55")

        eyec = self.get_theme_color("accent", "#ff2244" if ph >= 2 else "#ffd32a")
        for ex in (hx - 9, hx + 9):
            c.create_oval(ex - 5, hy - 10, ex + 5, hy - 2, fill="#ffffff", outline="#222222")
            c.create_oval(ex - 2, hy - 9, ex + 2, hy - 3, fill=eyec, outline="")
            c.create_line(ex, hy - 8, ex, hy - 4, width=2, fill="#000000")

    def _draw_cat(self, c, bx, by, ph, glitch, sq, t):
        fur = self.get_theme_color("primary", "#1e1e24" if (glitch or ph == 3) else ("#4b5563" if ph >= 2 else "#e67e22"))
        belly = self.get_theme_color("secondary", "#2c2c36" if ph >= 2 else "#fff5eb")
        eyec = self.get_theme_color("accent", "#ff2020" if ph >= 2 else "#2ecc71")

        c.create_oval(bx - 32, 150, bx + 32, 158, fill="#1a1410", outline="")

        tail_sw = math.sin(t * (12 if self.excited else 4)) * 14
        c.create_line(bx - 22, by + 22, bx - 40 + tail_sw, by + 10, bx - 36 + tail_sw * 1.5, by - 8,
                      width=6, fill=fur, capstyle="round", smooth=True)

        c.create_polygon(bx - 26, by - 26, bx - 34, by - 52, bx - 12, by - 36, fill=fur, outline="#2c1e14")
        c.create_polygon(bx - 24, by - 28, bx - 30, by - 48, bx - 14, by - 36, fill="#ffb8d2")
        c.create_polygon(bx + 12, by - 36, bx + 34, by - 52, bx + 26, by - 26, fill=fur, outline="#2c1e14")
        c.create_polygon(bx + 14, by - 36, bx + 30, by - 48, bx + 24, by - 28, fill="#ffb8d2")

        c.create_oval(bx - 32, by - 14 + sq, bx + 32, by + 32 - sq, fill=fur, outline="#2c1e14", width=1)
        c.create_oval(bx - 18, by - 2 + sq, bx + 18, by + 26 - sq, fill=belly, outline="")

        wig = math.sin(t * 10) * 4 if self.moving else 0
        c.create_oval(bx - 20, by + 26 + wig, bx - 6, by + 38 + wig, fill=belly, outline=fur)
        c.create_oval(bx + 6, by + 26 - wig, bx + 20, by + 38 - wig, fill=belly, outline=fur)

        c.create_oval(bx - 28, by - 40, bx + 28, by - 2, fill=fur, outline="#2c1e14", width=1)

        c.create_polygon(bx - 3, by - 14, bx + 3, by - 14, bx, by - 11, fill="#ff6b81")
        c.create_line(bx - 12, by - 16, bx - 32, by - 19, fill="#2c1e14", width=1)
        c.create_line(bx - 12, by - 13, bx - 32, by - 13, fill="#2c1e14", width=1)
        c.create_line(bx + 12, by - 16, bx + 32, by - 19, fill="#2c1e14", width=1)
        c.create_line(bx + 12, by - 13, bx + 32, by - 13, fill="#2c1e14", width=1)

        self._draw_standard_face(c, bx, by - 6, eyec, ph, glitch, t)

    def _draw_ghost(self, c, bx, by, ph, glitch, sq, t):
        ghost_col = self.get_theme_color("primary", "#241b36" if (glitch or ph == 3) else ("#35294a" if ph >= 2 else "#ebf6ff"))
        glow_col = self.get_theme_color("glow", "#bb86fc" if ph >= 2 else "#90caf9")
        eyec = self.get_theme_color("accent", "#ff2244" if ph >= 2 else "#2980b9")

        pts = [bx - 30, by - 22, bx - 32, by + 12]
        for k in range(7):
            gx = bx - 28 + k * 9
            gy = by + 32 + math.sin(t * 8 + k * 1.1) * 6
            pts += [gx, gy]
        pts += [bx + 32, by + 12, bx + 30, by - 22]
        c.create_polygon(pts, fill=ghost_col, outline=glow_col, width=2, smooth=True)

        c.create_oval(bx - 30, by - 44, bx + 30, by + 8, fill=ghost_col, outline="")

        h_bob = math.sin(t * 5) * 4
        c.create_oval(bx - 44, by + 2 + h_bob, bx - 30, by + 16 + h_bob, fill=ghost_col, outline=glow_col)
        c.create_oval(bx + 30, by + 2 - h_bob, bx + 44, by + 16 - h_bob, fill=ghost_col, outline=glow_col)

        self._draw_standard_face(c, bx, by - 8, eyec, ph, glitch, t)

    def _draw_dragon(self, c, bx, by, ph, glitch, sq, t):
        body = self.get_theme_color("primary", "#1f1624" if (glitch or ph == 3) else ("#5c101d" if ph >= 2 else "#8e1728"))
        belly = self.get_theme_color("secondary", "#d35400" if ph >= 2 else "#f39c12")
        eyec = self.get_theme_color("accent", "#ff2020" if ph >= 2 else "#f1c40f")

        c.create_oval(bx - 32, 150, bx + 32, 158, fill="#1f1116", outline="")

        flight_active = self.moving or t < self.dancing_until or self.excited or self.laser_active
        w_flap = math.sin(t * (18 if flight_active else 6)) * 14
        c.create_polygon(bx - 18, by - 10, bx - 52, by - 32 + w_flap, bx - 44, by - 12 + w_flap,
                         bx - 48, by + 8 + w_flap, bx - 18, by + 10, fill=body, outline="#ff4757")
        c.create_polygon(bx + 18, by - 10, bx + 52, by - 32 + w_flap, bx + 44, by - 12 + w_flap,
                         bx + 48, by + 8 + w_flap, bx + 18, by + 10, fill=body, outline="#ff4757")

        tx, ty = bx - 36, by + 24
        c.create_line(bx - 22, by + 20, tx, ty, width=5, fill=body, smooth=True)
        c.create_polygon(tx - 3, ty - 6, tx - 10, ty + 6, tx + 4, ty + 6, fill="#e74c3c")

        c.create_polygon(bx - 16, by - 36, bx - 32, by - 60, bx - 8, by - 44, fill="#f5cd79", outline="#b8860b", width=1)
        c.create_polygon(bx + 16, by - 36, bx + 32, by - 60, bx + 8, by - 44, fill="#f5cd79", outline="#b8860b", width=1)

        c.create_oval(bx - 30, by - 26 + sq, bx + 30, by + 30 - sq, fill=body, outline="#4a0c14", width=1)
        c.create_oval(bx - 16, by - 10 + sq, bx + 16, by + 26 - sq, fill=belly, outline="")
        for ry in range(int(by - 6), int(by + 22), 6):
            c.create_line(bx - 11, ry, bx + 11, ry, fill="#b33939", width=1)

        wig = math.sin(t * 10) * 4 if self.moving else 0
        c.create_line(bx - 12, by + 26, bx - 12 + wig, by + 40, width=5, fill=body, capstyle="round")
        c.create_line(bx + 12, by + 26, bx + 12 - wig, by + 40, width=5, fill=body, capstyle="round")

        c.create_polygon(bx, by - 46, bx + 4, by - 52, bx + 2, by - 44, fill="#f39c12")
        c.create_polygon(bx, by - 38, bx + 4, by - 44, bx + 2, by - 36, fill="#f39c12")

        self._draw_standard_face(c, bx, by - 4, eyec, ph, glitch, t)

    def _draw_mech(self, c, bx, by, ph, glitch, sq, t):
        hull_col = self.get_theme_color("primary", "#1e272e" if ph >= 2 else "#3d4852")
        screen_col = self.get_theme_color("secondary", "#0d1117")
        led_col = self.get_theme_color("accent", "#00d2d3" if ph < 2 else "#ff4757")

        c.create_oval(bx - 28, 150, bx + 28, 158, fill="#12161c", outline="")

        flame_len = 7 + math.sin(t * 22) * 5
        c.create_polygon(bx - 16, by + 26, bx - 8, by + 26, bx - 12, by + 26 + flame_len, fill=led_col)
        c.create_polygon(bx + 8, by + 26, bx + 16, by + 26, bx + 12, by + 26 + flame_len, fill=led_col)

        c.create_rectangle(bx - 18, by + 20, bx - 6, by + 26, fill="#2f3542", outline="#1e272e")
        c.create_rectangle(bx + 6, by + 20, bx + 18, by + 26, fill="#2f3542", outline="#1e272e")

        c.create_line(bx, by - 32, bx, by - 48, width=3, fill="#747d8c")
        dish_rot = math.sin(t * 4) * 5
        c.create_arc(bx - 10 + dish_rot, by - 56, bx + 10 + dish_rot, by - 44, start=180, extent=180, style="arc", width=2, outline="#a4b0be")
        c.create_oval(bx - 2, by - 58, bx + 2, by - 54, fill=led_col, outline="")

        c.create_oval(bx - 32, by - 32 + sq, bx + 32, by + 22 - sq, fill=hull_col, outline="#2f3542", width=2)
        for rx, ry in [(-22, -16), (22, -16), (-22, 10), (22, 10)]:
            c.create_oval(bx + rx - 2, by + ry - 2, bx + rx + 2, by + ry + 2, fill="#747d8c", outline="")

        c.create_rectangle(bx - 20, by - 16, bx + 20, by + 8, fill=screen_col, outline="#57606f", width=1)
        if t < self.dead_until:
            disp = "[x_x]"
        elif self.sleeping:
            disp = "[-_-]"
        elif t < self.happy_until or t < self.dancing_until:
            disp = "[^_^]"
        elif glitch:
            disp = "[#@!]"
        elif ph == 3:
            disp = "[ò_ó]"
        else:
            disp = "[o_o]"
        c.create_text(bx, by - 4, text=disp, fill=led_col, font=("Consolas", 10, "bold"))

    def _draw_jelly(self, c, bx, by, ph, glitch, sq, t):
        bell_col = self.get_theme_color("primary", "#00cec9" if ph < 2 else "#fd79a8")
        inner_col = self.get_theme_color("secondary", "#0984e3" if ph < 2 else "#6c5ce7")
        glow_col = self.get_theme_color("glow", "#81ecec" if ph < 2 else "#e84393")
        eyec = self.get_theme_color("accent", "#ffffff" if ph < 3 else "#ff1744")

        pulse = math.sin(t * 6) * 3 if self.moving else 0
        c.create_oval(bx - 32 - pulse, by - 36, bx + 32 + pulse, by + 12 + pulse, fill=bell_col, outline=glow_col, width=2)
        c.create_oval(bx - 20, by - 26, bx + 20, by + 4, fill=inner_col, outline="")

        for i in range(5):
            tx_base = bx - 22 + i * 11
            pts = [tx_base, by + 12]
            for seg in range(1, 5):
                wave = math.sin(t * 7 + i * 1.2 + seg * 0.9) * 8
                pts += [tx_base + wave, by + 12 + seg * 8]
            c.create_line(*pts, width=3, fill=bell_col, capstyle="round", smooth=True)

        self._draw_standard_face(c, bx, by - 10, eyec, ph, glitch, t)

    def _draw_fox(self, c, bx, by, ph, glitch, sq, t):
        fur_col = self.get_theme_color("primary", "#d35400" if ph < 2 else "#e17055")
        white_col = self.get_theme_color("secondary", "#ffffff")
        eyec = self.get_theme_color("accent", "#f1c40f" if ph < 2 else "#ff2244")

        c_tails = [math.sin(t * 5) * 14, math.sin(t * 5 + 0.9) * 12, math.sin(t * 5 - 0.9) * 12]
        for idx, sw in enumerate(c_tails):
            tx = bx - 26 - idx * 4
            ty = by + 18 - idx * 4
            c.create_line(tx, ty, tx - 18 + sw, ty - 12, tx - 14 + sw * 1.3, ty - 26, width=7, fill=fur_col, capstyle="round", smooth=True)
            c.create_line(tx - 18 + sw, ty - 12, tx - 14 + sw * 1.3, ty - 26, width=6, fill=white_col, capstyle="round", smooth=True)

        c.create_polygon(bx - 26, by - 26, bx - 34, by - 56, bx - 12, by - 36, fill=fur_col, outline="#2c1e14")
        c.create_polygon(bx - 28, by - 44, bx - 34, by - 56, bx - 22, by - 48, fill="#1e1e24")
        c.create_polygon(bx - 24, by - 28, bx - 28, by - 46, bx - 14, by - 36, fill="#ffeaa7")

        c.create_polygon(bx + 12, by - 36, bx + 34, by - 56, bx + 26, by - 26, fill=fur_col, outline="#2c1e14")
        c.create_polygon(bx + 22, by - 48, bx + 34, by - 56, bx + 28, by - 44, fill="#1e1e24")
        c.create_polygon(bx + 14, by - 36, bx + 28, by - 46, bx + 24, by - 28, fill="#ffeaa7")

        c.create_oval(bx - 30, by - 14 + sq, bx + 30, by + 32 - sq, fill=fur_col, outline="#2c1e14", width=1)
        c.create_oval(bx - 16, by - 2 + sq, bx + 16, by + 26 - sq, fill=white_col, outline="")
        c.create_oval(bx - 26, by - 40, bx + 26, by - 4, fill=fur_col, outline="#2c1e14", width=1)

        c.create_polygon(bx - 16, by - 16, bx + 16, by - 16, bx, by - 4, fill=white_col)
        c.create_polygon(bx - 3, by - 8, bx + 3, by - 8, bx, by - 5, fill="#111116")

        ff_bob = math.sin(t * 6) * 5
        ff_col = self.get_theme_color("glow", "#00d2d3" if ph < 2 else "#ff4757")
        c.create_text(bx - 38, by - 24 + ff_bob, text="🔥", font=("Segoe UI", 11), fill=ff_col)
        c.create_text(bx + 38, by - 24 - ff_bob, text="🔥", font=("Segoe UI", 11), fill=ff_col)

        self._draw_standard_face(c, bx, by - 8, eyec, ph, glitch, t)

    def _draw_frog(self, c, bx, by, ph, glitch, sq, t):
        skin_col = self.get_theme_color("primary", "#2ecc71" if ph < 2 else "#16a085")
        belly_col = self.get_theme_color("secondary", "#f1f2f6")
        eyec = self.get_theme_color("accent", "#f1c40f" if ph < 2 else "#ff4757")

        c.create_oval(bx - 34, by - 22 + sq, bx + 34, by + 32 - sq, fill=skin_col, outline="#1e824c", width=2)
        croak = math.sin(t * 8) * 5 if (self.excited or t < self.happy_until) else 0
        c.create_oval(bx - 18 - croak, by + 2 + sq, bx + 18 + croak, by + 28 - sq + croak, fill=belly_col, outline="")

        c.create_oval(bx - 38, by + 22, bx - 22, by + 36, fill=skin_col, outline="#1e824c")
        c.create_oval(bx + 22, by + 22, bx + 38, by + 36, fill=skin_col, outline="#1e824c")

        for ex in (bx - 16, bx + 16):
            c.create_oval(ex - 12, by - 44, ex + 12, by - 20, fill=skin_col, outline="#1e824c", width=2)
            c.create_oval(ex - 9, by - 41, ex + 9, by - 23, fill="#ffffff", outline="")
            c.create_oval(ex - 5, by - 36, ex + 5, by - 28, fill=eyec, outline="")
            c.create_oval(ex - 2, by - 34, ex + 2, by - 30, fill="#000000", outline="")

        c.create_arc(bx - 26, by - 12, bx + 26, by + 14, start=200, extent=140, style="arc", width=2, outline="#145a32")

    def _draw_bat(self, c, bx, by, ph, glitch, sq, t):
        fur_col = self.get_theme_color("primary", "#2f2038" if ph < 2 else "#191124")
        wing_col = self.get_theme_color("secondary", "#1c1424")
        eyec = self.get_theme_color("accent", "#e84393" if ph < 2 else "#ff1744")

        c.create_polygon(bx - 16, by - 34, bx - 30, by - 60, bx - 6, by - 42, fill=fur_col, outline="#140d1a")
        c.create_polygon(bx - 18, by - 36, bx - 28, by - 56, bx - 8, by - 44, fill="#ff7675")
        c.create_polygon(bx + 16, by - 34, bx + 30, by - 60, bx + 6, by - 42, fill=fur_col, outline="#140d1a")
        c.create_polygon(bx + 18, by - 36, bx + 28, by - 56, bx + 8, by - 44, fill="#ff7675")

        if self.sleeping:
            c.create_polygon(bx - 32, by - 10, bx, by + 34, bx - 26, by + 30, fill=wing_col, outline="#3d2c4d")
            c.create_polygon(bx + 32, by - 10, bx, by + 34, bx + 26, by + 30, fill=wing_col, outline="#3d2c4d")
        else:
            w_flap = math.sin(t * (18 if self.moving else 8)) * 14
            c.create_polygon(bx - 16, by, bx - 50, by - 26 + w_flap, bx - 44, by - 8 + w_flap,
                             bx - 48, by + 12 + w_flap, bx - 16, by + 14, fill=wing_col, outline="#3d2c4d")
            c.create_polygon(bx + 16, by, bx + 50, by - 26 + w_flap, bx + 44, by - 8 + w_flap,
                             bx + 48, by + 12 + w_flap, bx + 16, by + 14, fill=wing_col, outline="#3d2c4d")

        c.create_oval(bx - 26, by - 24 + sq, bx + 26, by + 30 - sq, fill=fur_col, outline="#140d1a", width=1)
        c.create_polygon(bx - 6, by - 10, bx - 3, by - 4, bx - 1, by - 10, fill="#ffffff")
        c.create_polygon(bx + 1, by - 10, bx + 3, by - 4, bx + 6, by - 10, fill="#ffffff")

        self._draw_standard_face(c, bx, by - 6, eyec, ph, glitch, t)

    def _draw_penguin(self, c, bx, by, ph, glitch, sq, t):
        fur = self.get_theme_color("primary", "#11141a" if (glitch or ph == 3) else ("#1e272e" if ph >= 2 else "#2d3436"))
        belly = self.get_theme_color("secondary", "#f1f2f6" if ph < 3 else "#3a3e47")
        accent = self.get_theme_color("accent", "#ff2244" if ph >= 2 else "#ff9f43")

        c.create_oval(bx - 30, 150, bx + 30, 158, fill="#12161f", outline="")

        # Flippers waddle / flap
        waddle = math.sin(t * (14 if self.moving else 6)) * 12
        c.create_polygon(bx - 24, by - 8, bx - 44, by + 12 + waddle, bx - 26, by + 20, fill=fur, outline="#111", smooth=True)
        c.create_polygon(bx + 24, by - 8, bx + 44, by + 12 - waddle, bx + 26, by + 20, fill=fur, outline="#111", smooth=True)

        # Webbed feet
        wig = math.sin(t * 10) * 4 if self.moving else 0
        c.create_oval(bx - 22, by + 26 + wig, bx - 6, by + 37 + wig, fill=accent, outline="#c0392b" if ph >= 2 else "#d35400")
        c.create_oval(bx + 6, by + 26 - wig, bx + 22, by + 37 - wig, fill=accent, outline="#c0392b" if ph >= 2 else "#d35400")

        # Tuxedo dome torso
        c.create_oval(bx - 28, by - 32 + sq, bx + 28, by + 30 - sq, fill=fur, outline="#111", width=1)
        c.create_oval(bx - 17, by - 16 + sq, bx + 17, by + 26 - sq, fill=belly, outline="")

        # Dapper bowtie / crest
        c.create_polygon(bx - 6, by - 16, bx + 6, by - 16, bx, by - 11, fill="#e74c3c" if ph < 2 else accent)
        c.create_polygon(bx - 5, by - 10, bx + 5, by - 10, bx, by - 15, fill="#e74c3c" if ph < 2 else accent)

        # Triangular beak
        c.create_polygon(bx - 6, by - 12, bx + 6, by - 12, bx, by - 4, fill=accent, outline="#c0392b" if ph >= 2 else "#d35400")

        eyec = accent if ph >= 2 else "#2d3436"
        self._draw_standard_face(c, bx, by - 6, eyec, ph, glitch, t)

    def _draw_shroom(self, c, bx, by, ph, glitch, sq, t):
        cap_col = self.get_theme_color("primary", "#e74c3c" if ph < 2 else ("#8e44ad" if ph == 2 else "#2c0e3a"))
        stem_col = self.get_theme_color("secondary", "#fdfefe" if ph < 3 else "#3a3a46")
        spore_col = self.get_theme_color("glow", "#ffeaa7" if ph < 2 else "#e056fd")
        eyec = self.get_theme_color("accent", "#2c3e50" if ph < 2 else "#ff2244")

        c.create_oval(bx - 24, 150, bx + 24, 157, fill="#181820", outline="")

        # Drifting spore particles
        for i in range(4):
            sp_x = bx + math.sin(t * 3 + i * 1.6) * (26 + i * 4)
            sp_y = by - 36 - ((t * 22 + i * 16) % 36)
            c.create_oval(sp_x - 2, sp_y - 2, sp_x + 2, sp_y + 2, fill=spore_col, outline="")

        # Stem & stubby feet
        c.create_rectangle(bx - 14, by - 4, bx + 14, by + 30, fill=stem_col, outline="#b2bec3", width=1)
        wig = math.sin(t * 10) * 3 if self.moving else 0
        c.create_oval(bx - 16, by + 26 + wig, bx - 3, by + 37 + wig, fill=stem_col, outline="#b2bec3")
        c.create_oval(bx + 3, by + 26 - wig, bx + 16, by + 37 - wig, fill=stem_col, outline="#b2bec3")

        # Bouncy mushroom cap
        bounce = math.sin(t * 8) * 4 if self.moving else math.sin(t * 3.5) * 2
        c.create_arc(bx - 42, by - 46 + bounce, bx + 42, by + 8 + bounce, start=0, extent=180, fill=cap_col, outline="#2c2c36", width=1.5)
        # Cap rim underside
        c.create_oval(bx - 42, by - 12 + bounce, bx + 42, by + 8 + bounce, fill="#ffeaa7" if ph < 2 else "#574b90", outline="#2c2c36", width=1)

        # Polka dots
        c.create_oval(bx - 26, by - 34 + bounce, bx - 14, by - 22 + bounce, fill=stem_col, outline="")
        c.create_oval(bx - 5, by - 43 + bounce, bx + 7, by - 31 + bounce, fill=stem_col, outline="")
        c.create_oval(bx + 18, by - 32 + bounce, bx + 30, by - 20 + bounce, fill=stem_col, outline="")
        c.create_oval(bx - 32, by - 18 + bounce, bx - 22, by - 8 + bounce, fill=stem_col, outline="")
        c.create_oval(bx + 22, by - 16 + bounce, bx + 32, by - 6 + bounce, fill=stem_col, outline="")

        # Face on the stem
        self._draw_standard_face(c, bx, by + 12, eyec, ph, glitch, t)

    def _draw_alien(self, c, bx, by, ph, glitch, sq, t):
        skin_col = self.get_theme_color("primary", "#6c5ce7" if ph < 2 else ("#20bf6b" if ph == 2 else "#1e1338"))
        dome_col = self.get_theme_color("secondary", "#a29bfe" if ph < 2 else ("#26de81" if ph == 2 else "#4834d4"))
        glow_col = self.get_theme_color("glow", "#00cec9" if ph < 2 else "#ff4757")
        eyec = self.get_theme_color("accent", "#fdcb6e" if ph < 2 else "#eb4d4b")

        # Antigravity hover beam
        pulse = math.sin(t * 10) * 4
        c.create_polygon(bx - 12, by + 24, bx + 12, by + 24, bx + 22 + pulse, by + 44, bx - 22 - pulse, by + 44,
                         fill="#00ffff" if ph < 2 else glow_col, outline="")

        # Levitating tentacle feet
        for idx in (-1, 0, 1):
            tw = math.sin(t * 7 + idx * 1.5) * 4
            c.create_line(bx + idx * 11, by + 20, bx + idx * 13 + tw, by + 34, width=3, fill=skin_col, capstyle="round")

        # 3 Stalk Antennas
        # Center antenna
        c.create_line(bx, by - 26, bx, by - 50, width=2.5, fill=skin_col)
        c.create_oval(bx - 5, by - 58, bx + 5, by - 48, fill=glow_col, outline="")
        # Left antenna
        c.create_line(bx - 14, by - 24, bx - 26, by - 46, width=2.5, fill=skin_col)
        c.create_oval(bx - 31, by - 52, bx - 21, by - 42, fill=glow_col, outline="")
        # Right antenna
        c.create_line(bx + 14, by - 24, bx + 26, by - 46, width=2.5, fill=skin_col)
        c.create_oval(bx + 21, by - 52, bx + 31, by - 42, fill=glow_col, outline="")

        # Smooth round alien body
        c.create_oval(bx - 32, by - 26 + sq, bx + 32, by + 24 - sq, fill=skin_col, outline="#2c2c54", width=1.5)
        c.create_oval(bx - 18, by - 10 + sq, bx + 18, by + 16 - sq, fill=dome_col, outline="")

        # 3 Curious googly eyes
        for ex, ey_off in ((bx - 16, 0), (bx, -4), (bx + 16, 0)):
            c.create_oval(ex - 6, by - 16 + ey_off, ex + 6, by - 4 + ey_off, fill="#ffffff", outline="#222222")
            if self.sleeping:
                c.create_line(ex - 5, by - 10 + ey_off, ex + 5, by - 10 + ey_off, width=2, fill=eyec)
            elif t < self.happy_until:
                c.create_arc(ex - 6, by - 16 + ey_off, ex + 6, by - 4 + ey_off, start=200, extent=140, style="arc", width=2, outline=eyec)
            else:
                c.create_oval(ex - 3, by - 14 + ey_off, ex + 3, by - 6 + ey_off, fill=eyec, outline="")
                c.create_oval(ex - 1, by - 12 + ey_off, ex + 1, by - 8 + ey_off, fill="#000000", outline="")

        # Alien mouth
        if t < self.happy_until or t < self.dancing_until:
            c.create_arc(bx - 8, by - 2, bx + 8, by + 10, start=200, extent=140, style="arc", width=2, outline=eyec)
        else:
            c.create_oval(bx - 3, by + 2, bx + 3, by + 7, fill="#2c2c54", outline="")

    def _draw_standard_face(self, c, bx, by, eyec, ph, glitch, t):
        if t < self.dead_until:
            for ex in (bx - 14, bx + 14):
                c.create_line(ex - 6, by - 16, ex + 6, by - 8, width=3, fill=eyec)
                c.create_line(ex - 6, by - 8, ex + 6, by - 16, width=3, fill=eyec)
        else:
            for ex in (bx - 14, bx + 14):
                if self.sleeping:
                    c.create_line(ex - 7, by - 12, ex + 7, by - 12, width=3, fill=eyec)
                elif t < self.happy_until or t < self.dancing_until:
                    c.create_arc(ex - 8, by - 20, ex + 8, by - 4,
                                 start=200, extent=140, style="arc", width=3, outline=eyec)
                elif glitch or ph == 3:
                    c.create_oval(ex - 7, by - 18, ex + 7, by - 4, fill=eyec, outline="#ff6666", width=1)
                    c.create_oval(ex - 2, by - 14, ex + 2, by - 10, fill="#ffffff", outline="")
                else:
                    r = 9 if self.staring else 8
                    c.create_oval(ex - r, by - 12 - r + 4, ex + r, by - 12 + r + 4, fill="#ffffff", outline="#333333")
                    if self.mon.have_pynput:
                        dx = self.mon.mouse[0] - (self.root.winfo_rootx() + ex)
                        dy = self.mon.mouse[1] - (self.root.winfo_rooty() + by - 12)
                        d = math.hypot(dx, dy) or 1
                        ox, oy = dx / d * 4, dy / d * 4
                    else:
                        ox, oy = math.sin(t) * 2, math.cos(t * 0.7) * 2
                    if not t < self.blink_until:
                        c.create_oval(ex + ox - 3.5, by - 12 + oy + 1,
                                      ex + ox + 3.5, by - 12 + oy + 8, fill=eyec, outline="")
                        c.create_oval(ex + ox - 1, by - 12 + oy + 2,
                                      ex + ox + 1, by - 12 + oy + 4, fill="#ffffff", outline="")

        # Mouth
        if glitch:
            pts = []
            for i in range(7): pts += [bx - 15 + i * 5, by + 8 + (i % 2) * 6]
            c.create_line(*pts, fill="#ff2020", width=2)
        elif t < self.happy_until or t < self.eating:
            c.create_arc(bx - 12, by + 2, bx + 12, by + 20,
                         start=200, extent=140, style="arc", width=2, outline=eyec)
        elif self.hunger > 70 and ph < 3:
            c.create_arc(bx - 10, by + 12, bx + 10, by + 26,
                         start=20, extent=140, style="arc", width=2, outline=eyec)
        elif ph < 3:
            c.create_arc(bx - 8, by + 6, bx + 8, by + 16,
                         start=200, extent=120, style="arc", width=2, outline=eyec)

    def _draw_accessory(self, c, bx, by, t):
        acc = self.accessory
        if acc == "tophat":
            c.create_rectangle(bx - 26, by - 44, bx + 26, by - 40, fill="#121216", outline="#2a2a35")
            c.create_rectangle(bx - 18, by - 70, bx + 18, by - 44, fill="#181820", outline="#2a2a35")
            c.create_rectangle(bx - 18, by - 49, bx + 18, by - 44, fill="#c91838", outline="")
            c.create_rectangle(bx - 4, by - 50, bx + 4, by - 43, fill="#ffd034", outline="")
        elif acc == "shades":
            # Pixel Thug Life Sunglasses
            c.create_polygon(bx - 26, by - 16, bx - 2, by - 16, bx - 4, by - 5, bx - 24, by - 5, fill="#050508", outline="#22222a")
            c.create_polygon(bx + 2, by - 16, bx + 26, by - 16, bx + 24, by - 5, bx + 4, by - 5, fill="#050508", outline="#22222a")
            c.create_line(bx - 3, by - 13, bx + 3, by - 13, width=2, fill="#050508")
            c.create_line(bx - 22, by - 14, bx - 14, by - 7, fill="#ffffff", width=2)
            c.create_line(bx + 6, by - 14, bx + 14, by - 7, fill="#ffffff", width=2)
        elif acc == "crown":
            pts = [bx - 20, by - 40, bx - 22, by - 56, bx - 10, by - 46, bx, by - 60, bx + 10, by - 46, bx + 22, by - 56, bx + 20, by - 40]
            c.create_polygon(pts, fill="#ffd034", outline="#c49a15", width=2)
            c.create_rectangle(bx - 20, by - 43, bx + 20, by - 39, fill="#e89812", outline="")
            c.create_oval(bx - 3, by - 52, bx + 3, by - 46, fill="#e52b50", outline="")
            c.create_oval(bx - 14, by - 47, bx - 10, by - 43, fill="#2b82e5", outline="")
            c.create_oval(bx + 10, by - 47, bx + 14, by - 43, fill="#2b82e5", outline="")
        elif acc == "horns":
            c.create_polygon(bx - 20, by - 26, bx - 34, by - 48, bx - 14, by - 34, fill="#dd1830", outline="#880010", width=1)
            c.create_polygon(bx + 20, by - 26, bx + 34, by - 48, bx + 14, by - 34, fill="#dd1830", outline="#880010", width=1)
        elif acc == "wizard":
            c.create_oval(bx - 28, by - 44, bx + 28, by - 36, fill="#241b4a", outline="#3a2e70")
            c.create_polygon(bx - 18, by - 42, bx + 6, by - 76, bx + 18, by - 42, fill="#342868", outline="#4b3b90")
            c.create_line(bx - 18, by - 44, bx + 18, by - 44, fill="#ffd034", width=3)
            c.create_text(bx + 1, by - 56, text="★", fill="#ffd034", font=("Arial", 9, "bold"))
        elif acc == "halo":
            bob = math.sin(t * 3) * 2
            c.create_oval(bx - 22, by - 58 + bob, bx + 22, by - 48 + bob, fill="", outline="#ffe055", width=4)
            c.create_oval(bx - 22, by - 58 + bob, bx + 22, by - 48 + bob, fill="", outline="#ffffff", width=1)
        elif acc == "bow":
            c.create_polygon(bx + 14, by - 34, bx + 28, by - 44, bx + 28, by - 24, fill="#ff4d79", outline="#cc2250")
            c.create_polygon(bx + 14, by - 34, bx, by - 44, bx, by - 24, fill="#ff4d79", outline="#cc2250")
            c.create_oval(bx + 10, by - 38, bx + 18, by - 30, fill="#ff7599", outline="#cc2250")

    def _draw_bubble(self, c, t):
        if t < self.bubble_until and self.bubble:
            tid = c.create_text(W // 2, 16, text=self.bubble, justify="center",
                                width=W - 16, font=("Segoe UI", 9, "bold"),
                                fill="#ffffff" if self.phase >= 2 else "#3a2b33")
            x0, y0, x1, y1 = c.bbox(tid)
            bg = "#1c1c22" if self.phase >= 2 else "#fff6fa"
            border = "#3a2b33" if self.phase >= 2 else "#e8cbd8"
            rid = c.create_rectangle(x0 - 6, y0 - 3, x1 + 6, y1 + 3, fill=bg, outline=border)
            c.tag_lower(rid, tid)

    # ------------------------------------------------------------- windows --
    def _menu(self, event):
        m = tk.Menu(self.root, tearoff=0)

        # Feed Submenu
        feed_m = tk.Menu(m, tearoff=0)
        feed_m.add_command(label="🍩 Donut (+Sweet)", command=lambda: self.feed("donut"))
        feed_m.add_command(label="☕ Espresso (+Zoomies)", command=lambda: self.feed("coffee"))
        feed_m.add_command(label="🍕 Pizza (Full Feast)", command=lambda: self.feed("pizza"))
        feed_m.add_command(label="🖤 Shadow Void (+Chaos)", command=lambda: self.feed("void"))
        m.add_cascade(label="Snack Cafe", menu=feed_m)

        m.add_command(label="Pet (Pat)", command=self.pat)

        # Activities Submenu
        act_m = tk.Menu(m, tearoff=0)
        act_m.add_command(label="🔴 Laser Pointer Chase", command=self.start_laser_game)
        act_m.add_command(label="🤸 Do a Backflip", command=self.do_flip)
        act_m.add_command(label="💃 Dance Party", command=self.do_dance)
        act_m.add_command(label="✊ Rock-Paper-Scissors", command=self.play_rps)
        act_m.add_command(label="🔮 Ask Fortune (8-Ball)", command=self.ask_fortune)
        act_m.add_command(label="😵 Play Dead", command=self.play_dead)
        act_m.add_separator()
        act_m.add_command(label="⏱️ 25m Focus Session", command=lambda: self.start_focus(25))
        act_m.add_command(label="⏱️ 15m Quick Focus", command=lambda: self.start_focus(15))
        m.add_cascade(label="Activities & Games", menu=act_m)

        # Wardrobe Submenu
        style_m = tk.Menu(m, tearoff=0)
        for acc_name, label in [
            ("none", "❌ None"),
            ("tophat", "🎩 Top Hat"),
            ("shades", "😎 Cyber Shades"),
            ("crown", "👑 Royal Crown"),
            ("horns", "😈 Devil Horns"),
            ("wizard", "🧙 Wizard Hat"),
            ("halo", "😇 Angel Halo"),
            ("bow", "🎀 Cute Bow")
        ]:
            style_m.add_command(label=label, command=lambda a=acc_name: self.set_accessory(a))
        m.add_cascade(label="Wardrobe (Hats)", menu=style_m)

        # Movement Mode Submenu
        move_m = tk.Menu(m, tearoff=0)
        move_m.add_command(label="🌌 Full Screen Roam" + (" ✓" if self.move_mode == "free_roam" else ""),
                           command=lambda: self.set_move_mode("free_roam"))
        move_m.add_command(label="🐾 Follow Cursor" + (" ✓" if self.move_mode == "follow_cursor" else ""),
                           command=lambda: self.set_move_mode("follow_cursor"))
        move_m.add_command(label="📌 Taskbar Floor" + (" ✓" if self.move_mode == "taskbar" else ""),
                           command=lambda: self.set_move_mode("taskbar"))
        m.add_cascade(label="Movement (Flight)", menu=move_m)

        # Pet Species Submenu
        pet_m = tk.Menu(m, tearoff=0)
        for sp_id, info in PET_SPECIES.items():
            mark = " ✓" if self.species == sp_id else ""
            pet_m.add_command(label=f"{info['icon']} {info['name']} ({info['title']}){mark}",
                              command=lambda s=sp_id: self.set_species(s))
        m.add_cascade(label="Choose Pet Species", menu=pet_m)

        # Color Theme Submenu
        theme_m = tk.Menu(m, tearoff=0)
        for th_id, th_info in COLOR_THEMES.items():
            mark = " ✓" if self.color_theme == th_id else ""
            theme_m.add_command(label=f"{th_info['icon']} {th_info['name']}{mark}",
                                command=lambda t=th_id: self.set_color_theme(t))
        m.add_cascade(label="🎨 Color Theme", menu=theme_m)

        m.add_separator()
        m.add_command(label="📊 Pet Profile & Stats", command=self.show_stats)
        m.add_command(label="🛡️ File Recovery", command=self.show_recovery)
        m.add_separator()
        m.add_command(label="👁️ Hide to Hidden Icons Tray", command=self.toggle_visibility)
        autostart_mark = " ✓" if self.is_autostart_enabled() else ""
        m.add_command(label=f"🚀 Start with Windows{autostart_mark}", command=self.toggle_autostart)
        m.add_separator()
        m.add_command(label="Say goodnight & quit (Off)", command=self.quit_nice)
        m.add_command(label="Quit completely (rude)", command=self.quit_rude)
        m.tk_popup(event.x_root, event.y_root)

    def set_accessory(self, acc):
        self.accessory = acc
        self.speak(f"Equipped {acc}!", 3)
        self._spawn_particle(80, 70, count=8, char="✦", color="#ffe04b")
        self._save()

    def set_move_mode(self, mode):
        self.move_mode = mode
        names = {"free_roam": "Full Screen Roam", "follow_cursor": "Follow Cursor", "taskbar": "Taskbar Floor"}
        self.speak(f"Movement: {names.get(mode, mode)}!", 3)
        self.target_roam_x = self.x
        self.target_roam_y = self.y
        self.next_roam_pick = 0
        self._save()

    def set_species(self, sp):
        if sp in PET_SPECIES:
            self.species = sp
            sp_info = PET_SPECIES[sp]
            # If current name matches another species' default name, switch to this species' name
            for other_sp, info in PET_SPECIES.items():
                if self.pet_name == info["name"]:
                    self.pet_name = sp_info["name"]
                    break
            self.speak(f"{sp_info['icon']} Transformed into {self.pet_name} ({sp_info['title']})!", 4)
            self._spawn_particle(80, 100, count=15, char="★", color="#ffe04b")
            self._save()
            self._update_tray_icon()

    def show_stats(self):
        win = tk.Toplevel(self.root)
        win.title(f"{self.pet_name}'s Profile")
        win.geometry("380x620")
        win.configure(bg="#15151c")
        win.attributes("-topmost", True)

        header = tk.Frame(win, bg="#1e1e28", pady=10)
        header.pack(fill="x")

        sp_info = PET_SPECIES.get(self.species, PET_SPECIES["shadow"])
        curr_theme = COLOR_THEMES.get(self.color_theme, COLOR_THEMES["default"])
        title_lbl = tk.Label(header, text=f"{sp_info['icon']} {self.pet_name} [Lv. {self.level}]",
                             font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#1e1e28")
        title_lbl.pack()

        sub_lbl = tk.Label(header, text=f"Species: {sp_info['title']}  •  Accessory: {self.accessory.title()}\nTheme: {curr_theme['icon']} {curr_theme['name']}",
                           font=("Segoe UI", 8), fg="#9999aa", bg="#1e1e28")
        sub_lbl.pack()

        def rename():
            new_name = simpledialog.askstring("Rename Pet", "Enter new name for your pet:",
                                              initialvalue=self.pet_name, parent=win)
            if new_name and new_name.strip():
                self.pet_name = new_name.strip()
                title_lbl.config(text=f"{sp_info['icon']} {self.pet_name} [Lv. {self.level}]")
                self.speak(f"Call me {self.pet_name}!", 4)
                self._save()
                self._update_tray_icon()

        tk.Button(header, text="✏️ Rename Pet", font=("Segoe UI", 8), bg="#2c2c3c", fg="#ddddff",
                  activebackground="#444455", command=rename).pack(pady=4)

        body_f = tk.Frame(win, bg="#15151c", padx=14, pady=6)
        body_f.pack(fill="both", expand=True)

        # Species Switcher Grid inside profile
        spec_frame = tk.Frame(body_f, bg="#15151c")
        spec_frame.pack(fill="x", pady=(2, 4))
        tk.Label(spec_frame, text="Select Species:", font=("Segoe UI", 8, "bold"),
                 fg="#aaaaee", bg="#15151c").pack(anchor="w", pady=(0, 2))
        btn_grid = tk.Frame(spec_frame, bg="#15151c")
        btn_grid.pack(fill="x")
        row, col = 0, 0
        for sp_id, sinfo in PET_SPECIES.items():
            btn_bg = "#4834d4" if self.species == sp_id else "#222230"
            btn = tk.Button(btn_grid, text=f"{sinfo['icon']} {sinfo['name']}",
                            font=("Segoe UI", 8), bg=btn_bg, fg="#ffffff",
                            activebackground="#686de0", bd=0, padx=2, pady=2,
                            command=lambda s=sp_id, w=win: (self.set_species(s), w.destroy(), self.show_stats()))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            col += 1
            if col > 3:
                col = 0; row += 1
        for i in range(4):
            btn_grid.columnconfigure(i, weight=1)

        # Color Theme Switcher Grid inside profile
        theme_frame = tk.Frame(body_f, bg="#15151c")
        theme_frame.pack(fill="x", pady=(4, 6))
        tk.Label(theme_frame, text=f"Color Palette ({curr_theme['name']}):", font=("Segoe UI", 8, "bold"),
                 fg="#aaaaee", bg="#15151c").pack(anchor="w", pady=(0, 2))
        th_grid = tk.Frame(theme_frame, bg="#15151c")
        th_grid.pack(fill="x")
        t_row, t_col = 0, 0
        for th_id, th_info in COLOR_THEMES.items():
            btn_bg = "#6c5ce7" if self.color_theme == th_id else "#222230"
            btn = tk.Button(th_grid, text=f"{th_info['icon']} {th_info['name'].split()[0]}",
                            font=("Segoe UI", 8), bg=btn_bg, fg="#ffffff",
                            activebackground="#a29bfe", bd=0, padx=2, pady=2,
                            command=lambda t=th_id, w=win: (self.set_color_theme(t), w.destroy(), self.show_stats()))
            btn.grid(row=t_row, column=t_col, padx=2, pady=2, sticky="nsew")
            t_col += 1
            if t_col > 3:
                t_col = 0; t_row += 1
        for i in range(4):
            th_grid.columnconfigure(i, weight=1)

        def add_bar(label, val, col):
            f = tk.Frame(body_f, bg="#15151c")
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"{label:<10} {int(val)}%", font=("Consolas", 8, "bold"),
                     fg="#cccccc", bg="#15151c").pack(anchor="w")
            c = tk.Canvas(f, height=7, bg="#2a2a38", highlightthickness=0)
            c.pack(fill="x")
            pct = max(0, min(100, val))
            c.create_rectangle(0, 0, int(3.2 * pct), 7, fill=col, outline="")

        xp_pct = self.xp % 100
        add_bar(f"XP ({self.xp} total)", xp_pct, "#ffd034")
        add_bar("Hunger", self.hunger, "#e55039")
        add_bar("Trust", self.trust, "#4a69bd")
        add_bar("Chaos/Darkness", self.corruption, "#8c7ae6")

        stats_lbl = tk.Label(body_f, text=f"Patted: {self.stats_pats}x  •  Fed: {self.stats_fed}x",
                             font=("Segoe UI", 8), fg="#777788", bg="#15151c")
        stats_lbl.pack(pady=(4, 2))

        tk.Label(body_f, text="— Recent Memories —", font=("Segoe UI", 8, "bold"),
                 fg="#aaaaee", bg="#15151c").pack(pady=(4, 2))

        mem_box = tk.Text(body_f, font=("Consolas", 8), height=4, bg="#101015", fg="#bbbbcc", bd=0)
        mem_box.pack(fill="x")
        for (m,) in self.store.memories(5):
            mem_box.insert("end", f" • {m}\n")
        mem_box.config(state="disabled")

    def show_recovery(self):
        win = tk.Toplevel(self.root)
        win.title("PET.EXE — Recovery")
        win.geometry("300x260")
        win.configure(bg="#181820")
        win.attributes("-topmost", True)

        tk.Label(win, text="— PET'S NEST —", font=("Consolas", 11, "bold"), fg="#ffffff", bg="#181820").pack(pady=(12, 4))
        if not self.chaos.manifest:
            tk.Label(win, text="(empty. it took nothing… yet.)",
                     font=("Consolas", 9), fg="#888899", bg="#181820").pack(pady=8)
        else:
            for m in self.chaos.manifest:
                tag = "" if not m["new"].startswith("SAFE:") else " (claimed)"
                tk.Label(win, font=("Consolas", 9), fg="#ff9999", bg="#181820",
                         text=os.path.basename(m["orig"]) + tag).pack()

        tk.Button(win, text="Feed & Take Everything Back", bg="#3a3a4c", fg="#ffffff",
                  activebackground="#505068",
                  command=lambda: (self.feed("snack"), win.destroy())).pack(pady=14)

    # -------------------------------------------------------- system tray ---
    def _create_tray_image(self):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        p_col = self.get_theme_color("primary", "#1e1e28")
        a_col = self.get_theme_color("accent", "#ff2244")
        g_col = self.get_theme_color("glow", a_col)

        d.ellipse((3, 3, 61, 61), fill=None, outline=g_col, width=3)
        d.ellipse((7, 7, 57, 57), fill=p_col, outline=None)
        d.ellipse((19, 23, 27, 33), fill=a_col)
        d.ellipse((37, 23, 45, 33), fill=a_col)
        d.ellipse((22, 25, 25, 28), fill="#ffffff")
        d.ellipse((40, 25, 43, 28), fill="#ffffff")
        d.arc((22, 34, 42, 46), start=20, end=160, fill=a_col, width=2)
        return img

    def _update_tray_icon(self):
        if hasattr(self, "tray_icon") and self.tray_icon:
            try:
                self.tray_icon.icon = self._create_tray_image()
                sp_info = PET_SPECIES.get(self.species, PET_SPECIES["shadow"])
                state_str = " (Hidden)" if not getattr(self, "_visible", True) else ""
                self.tray_icon.title = f"PET.EXE — {self.pet_name} ({sp_info['title']}) [Lv.{self.level}]{state_str}"
            except Exception:
                pass

    def _setup_tray(self):
        if not HAVE_PYSTRAY:
            return
        try:
            sp_info = PET_SPECIES.get(self.species, PET_SPECIES["shadow"])
            img = self._create_tray_image()

            def on_toggle_click(icon, _):
                self.root.after(0, self.toggle_visibility)

            def on_summon_click(icon, _):
                self.root.after(0, self.summon_to_cursor)

            def on_profile_click(icon, _):
                self.root.after(0, self.show_stats)

            def on_feed_click(kind):
                return lambda icon, _: self.root.after(0, lambda: self.feed(kind))

            def on_autostart_click(icon, _):
                self.root.after(0, self.toggle_autostart)

            def on_quit_click(icon, _):
                self.root.after(0, self.quit_nice)

            tray_menu = menu(
                item(lambda _: "👁️ Hide Pet" if getattr(self, "_visible", True) else "👁️ Show Pet", on_toggle_click, default=True),
                item("📍 Bring to Cursor", on_summon_click),
                menu.SEPARATOR,
                item("📊 Pet Profile & Stats", on_profile_click),
                item("🍖 Snack Cafe", menu(
                    item("🍩 Donut", on_feed_click("donut")),
                    item("☕ Espresso", on_feed_click("coffee")),
                    item("🍕 Pizza", on_feed_click("pizza")),
                    item("🖤 Void Snack", on_feed_click("void")),
                )),
                menu.SEPARATOR,
                item("🚀 Start with Windows", on_autostart_click, checked=lambda _: self.is_autostart_enabled()),
                menu.SEPARATOR,
                item("❌ Quit & Turn Off", on_quit_click),
            )

            self.tray_icon = pystray.Icon(
                "pet_exe",
                img,
                f"PET.EXE — {self.pet_name} ({sp_info['title']}) [Lv.{self.level}]",
                tray_menu
            )
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"[pet] tray init notice: {e}")
            self.tray_icon = None

    def toggle_visibility(self):
        self._visible = not getattr(self, "_visible", True)
        if self._visible:
            self.root.deiconify()
            self.speak("I'm back! ✨", 3)
        else:
            self.root.withdraw()
        self._update_tray_icon()

    def summon_to_cursor(self):
        if not getattr(self, "_visible", True):
            self.toggle_visibility()
        mx, my = self.mon.mouse
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.x = max(10, min(sw - W - 10, mx - W // 2))
        self.y = max(10, min(sh - H - 10, my - H // 2 - 20))
        self.vx = 0
        self.vy = 0
        self.root.geometry(f"{W}x{H}+{int(self.x)}+{int(self.y)}")
        self.speak("You called? ✨", 3)
        self._spawn_particle(80, 100, count=15, char="★", color="#ffe04b")

    def _startup_vbs_path(self):
        startup_dir = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        return os.path.join(startup_dir, "PetEXE.vbs")

    def is_autostart_enabled(self):
        return os.path.isfile(self._startup_vbs_path())

    def toggle_autostart(self):
        vbs_path = self._startup_vbs_path()
        if self.is_autostart_enabled():
            try:
                os.remove(vbs_path)
                self.speak("Autostart disabled! ❌", 3)
            except Exception as e:
                print(f"[pet] error removing autostart: {e}")
        else:
            try:
                os.makedirs(os.path.dirname(vbs_path), exist_ok=True)
                script_path = os.path.abspath(__file__)
                content = (
                    'Set WshShell = CreateObject("WScript.Shell")\n'
                    f'WshShell.Run "pythonw.exe ""{script_path}""", 0, False\n'
                )
                with open(vbs_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.speak("Will start with Windows! 🚀", 3)
            except Exception as e:
                print(f"[pet] error enabling autostart: {e}")
        self._update_tray_icon()

    # --------------------------------------------------------------- quits --
    def quit_nice(self):
        self.store.set("last_quit", "nice")
        self.corruption = max(0, self.corruption - 1)
        self._shutdown()

    def quit_rude(self):
        self.store.set("last_quit", "rude")
        self.corruption = min(100, self.corruption + 5)
        self.store.remember("grudge", "left without saying goodnight")
        self._shutdown()

    def _shutdown(self):
        self._save()
        if hasattr(self, "tray_icon") and self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        if hasattr(self, "mon") and self.mon:
            try:
                self.mon.stop()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass
        os._exit(0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    PetApp().run()
