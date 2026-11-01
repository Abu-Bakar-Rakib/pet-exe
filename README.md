# 🐾 PET.EXE — Procedural Cyber Desktop Companion

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows&logoColor=white)](https://microsoft.com)
[![Dependencies](https://img.shields.io/badge/Dependencies-Tkinter%20%7C%20pynput-orange.svg)](#-installation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An animated, multi-species procedural desktop companion for Windows. Built in pure Python using zero heavy game engines — featuring transparent window keying, smooth vector animations, 14 unique creatures, 12 dynamic color themes, physics-based dragging, mini-games, and a progressive Tamagotchi evolution system.

---
<img width="150" height="170" alt="image" src="https://github.com/user-attachments/assets/9c3013e6-2c2e-4021-88e2-d70bf5d880ab" />
<img width="136" height="123" alt="image" src="https://github.com/user-attachments/assets/0490158a-6a78-40ff-8b7c-c1c3109e4218" />
<img width="131" height="189" alt="image" src="https://github.com/user-attachments/assets/329c4e3d-b4d3-4abc-8424-3b53ed822f0a" />
<img width="95" height="193" alt="image" src="https://github.com/user-attachments/assets/edaa1a96-8321-4ae3-af61-a9b2dc1cab34" />
<img width="112" height="130" alt="image" src="https://github.com/user-attachments/assets/ab10c773-281d-42f0-bcde-580644c71298" />
<img width="106" height="103" alt="image" src="https://github.com/user-attachments/assets/2731e2fa-b8c4-42eb-a5ff-a1a7d521fee1" />
<img width="83" height="112" alt="image" src="https://github.com/user-attachments/assets/4df40e64-7fab-4d9c-ac82-8c7ce77a8ed5" />
<img width="80" height="136" alt="image" src="https://github.com/user-attachments/assets/c66ec87c-5c1d-42a8-8875-6c4e431f70ce" />

## 🌟 Highlights

- **🪟 Pure Vector Transparency**: Runs seamlessly above all open windows with transparent color keying and zero border chrome.
- **🐾 14 Distinct Pet Species**: Kuro (Shadow Gremlin), Cipher (Cyber Agent), Viper (Cyber Serpent), Neko (Kitty), Ignis (Wyvern), Sparky (Drone), Inky (Jellyfish), Rox (Kitsune), and more!
- **🎨 12 Color Themes**: Instant 1-click palette swaps including Neon Cyberpunk, Midnight Void, Solar Gold, Toxic Emerald, Matrix Hacker, and Sunset Vaporwave.
- **🌌 3 Movement Modes**: Full-screen 2D free flight roaming, cursor-stalking companion, or grounded taskbar floor walker.
- **🎯 2D Laser Pointer Minigame**: Turn your mouse into an active red laser dot that your pet tracks, pounces on, and chases across your entire monitor.
- **🎮 Built-in Activities**: Backflips, Dance Parties, Rock-Paper-Scissors, Fortune Teller (8-Ball), and Playing Dead.
- **⏱️ Focus Companion**: Built-in 15m and 25m Pomodoro productivity sessions with animated timers.
- **🎩 Wardrobe & Hats**: Equip Top Hats, Cyber Shades, Royal Crowns, Devil Horns, Wizard Hats, Angel Halos, and Cute Bows.
- **🧠 100% Offline SQLite Storage**: Real-time hunger, trust, XP leveling, pat counters, and persistent activity logging stored locally in `~/.pet_exe/pet.db` — runs completely offline with zero internet needed.
- **🎛️ Windows System Tray ("Hidden Icons")**: Sits quietly in your Windows taskbar tray (`^`) with quick controls to Show/Hide, Bring to Cursor, Feed, Profile, and Start on PC Boot.
- **🛑 Clean Quit & Off Switch**: Selecting "Quit" terminates all background threads and processes instantly — when you turn it off, it is completely off.
- **🛑 Global Emergency Kill Switch**: Type `"sit boy"` anywhere on your PC at any time to instantly pacify and freeze your pet.

---

## 🐾 Species Roster

| Icon | Species | Default Name | Unique Traits & Animations |
| :---: | :--- | :--- | :--- |
| 🖤 | **Shadow Gremlin** | Kuro | Void wisp with fluttering wings, blinking red eyes, and floating idle bob |
| 🕵️ | **Cyber Agent** | Cipher | Secret agent in a trench coat & tie, animated cyan/red scanning visor & blinking earpiece |
| 🐍 | **Cyber Serpent** | Viper | Articulated multi-segment body with sinusoidal S-curve slithering, coiling sleep & flicking tongue |
| 🐱 | **Desktop Kitty** | Neko | Playful feline with perky ears, swishing tail, paws, whiskers, and cute `:3` expression |
| 👻 | **Spectral Wisp** | Phantom | Ethereal spirit floating with a wavy translucent tail and spirit motes |
| 🐉 | **Mini Wyvern** | Ignis | Winged dragon with flapping bat wings, golden horns, flame tail, and belly ridges |
| 🤖 | **Cyber Drone** | Sparky | Floating robot drone with twin thruster flame exhaust and digital CRT matrix face `[o_o]` |
| 🐙 | **Bio-Jellyfish** | Inky | Bioluminescent deep-sea jellyfish with pulsating bell and 5 undulating trailing tentacles |
| 🦊 | **Spirit Kitsune** | Rox | Mystic fox with 3 independent swishing bushy tails and floating foxfire flames |
| 🐸 | **Derpy Frog** | Froggo | Wide-mouthed frog with bulging googly eyes, expandable croak throat sac & webbed feet |
| 🦇 | **Vampire Bat** | Vlad | Gothic bat with velvet ears, cute fangs, and scalloped flapping wings / folded sleep cloak |
| 🐧 | **Royal Penguin** | Pippin | Tuxedo emperor penguin with waddling webbed feet, flapping flippers, and orange beak |
| 🍄 | **Sprout Mushroom** | Spore | Woodland mushroom with bouncy polka-dot cap and drifting glowing spore motes |
| 👾 | **Cosmic Martian** | Zog | Extraterrestrial traveler with 3 stalk antennas, 3 googly eyes, and pulsing hover beam |

---

## 🎨 Color Palettes

Switch palettes on the fly to recolor your pet's body, accents, and glows:

- ✨ **Default (Species)** — Authentic natural tones
- 🔮 **Neon Cyberpunk** — Hot neon magenta, midnight violet & electric cyan
- 🖤 **Midnight Void** — Obsidian black, dark slate & crimson accents
- ☀️ **Solar Gold** — Radiant amber, bronze & warm solar highlights
- 🌿 **Toxic Emerald** — Radioactive green, deep forest & lime glow
- 🌸 **Pastel Dream** — Cherry blossom pink, blush & lavender glow
- ❄️ **Arctic Frost** — Glacial cyan, polar navy & pure white
- 💜 **Amethyst Phantom** — Royal purple, mystic shadow & bright violet
- 🩸 **Crimson Blood** — Deep wine red, dark scarlet & blood glow
- 🌴 **Sunset Vaporwave** — Retro synthwave hot pink, ocean teal & neon lime
- 💻 **Matrix Hacker** — Classic green phosphor terminal with dark hacker casing
- ✒️ **Monochrome Ink** — Minimalist matte ink black, clean white & slate gray

---

## 🚀 Installation & Running

### Requirements
- **OS**: Windows 10 or Windows 11
- **Python**: Version 3.10 or higher
- **Libraries**: `pynput`, `pystray`, `pillow` (installed automatically via pip)
- **Offline**: 100% offline capable (no cloud API or network required)



---

## 🕹️ Controls & Interactions

| Action | Control | Description |
| :--- | :--- | :--- |
| **Pet / Pat** | `Left-Click` | Pets your creature, increases trust, and triggers cute heart particles |
| **Drag & Fling** | `Click + Drag` | Pick up your pet and throw it across the screen with real momentum physics |
| **Main Menu** | `Right-Click` | Access Snack Cafe, Activities, Wardrobe, Species, Palettes, and Stats |
| **Laser Chase** | Right-Click → `🔴 Laser Pointer Chase` | Chase your cursor across the entire screen! Catch it 3 times to win XP |
| **Species Picker** | Right-Click → `Choose Pet Species` | Instant 1-click transformation into any of the 14 species |
| **Palette Picker** | Right-Click → `🎨 Color Theme` | Instant 1-click recoloring across all body parts |
| **Emergency Calm** | Type `"sit boy"` | Global kill switch — calms, freezes, and returns the pet to safe mode |

---

## 📂 Architecture

- **Single-File Simplicity**: Everything runs inside self-contained [`pet.py`](pet.py) without requiring assets, sprite sheets, or game engines.
- **Procedural Graphics**: All characters, faces, hats, particles, and speech bubbles are procedurally calculated using Tkinter Canvas vector math.
- **Persistence Layer**: Pet stats, evolution level, memories, and settings are saved automatically in SQLite at `~/.pet_exe/pet.db`.
- **Safe Mode**: Desktop icon borrowing / chaos mechanics operate in simulated safe mode by default.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

