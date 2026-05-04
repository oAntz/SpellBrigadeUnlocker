# The Spell Brigade - Save Unlocker

Unlock everything in The Spell Brigade without grinding.

---

## What It Unlocks

- All quests completed (all 7 tabs: Missions, Wizards, Spells, Outfits, Scrolls, Ascension, Misc)
- All outfits and skins
- All covenants (sets characters to Prestige 2 + ascend-ready)
- All upgrades maxed
- All infusion elements
- All artifacts, objectives, and world difficulties
- 9,999,999 gold
- Steam achievements sync automatically on game launch

Works on brand new saves and existing saves. Your save is always backed up first.

---

## How to Use

### 1. Install Python
Download from https://www.python.org/downloads/ — check **"Add Python to PATH"** during install.

### 2. Install the required library
Open Command Prompt and run:
```
pip install pycryptodome
```

### 3. Close the game completely

### 4. Run the unlocker
Double-click `spell_brigade_unlocker.py` or run from Command Prompt:
```
python spell_brigade_unlocker.py
```

### 5. Press 1 for Unlock All, then Y to confirm

### 6. Launch the game

---

## Options

### 1. Unlock All
Everything listed above in one shot. Best for most people.

### 2. Custom Prestige
Set a specific prestige level for all characters. Prestige is the progression system where you reset a character's rank to gain permanent bonuses and new abilities. Higher prestige = stronger characters. Prestige 2 unlocks all covenants (passive perks).

### 3. Challenges Only
Complete every quest across all 7 tabs (Missions, Wizards, Spells, Outfits, Scrolls, Ascension, Misc) without changing your characters. Good if you just want the quest rewards but want to keep leveling characters yourself.

### 4. Infusions Only
Discover all 21 elements used in the infusion system. Infusions are elemental combinations you normally find during gameplay that boost your spells.

### 5. Ascend-Ready Only
Set all characters to Rank 10 (max rank) so they're ready to ascend. Ascending is when you reset a character's rank back to 1 in exchange for a prestige level. This option doesn't actually ascend them — it puts them at the doorstep so you can do it yourself in-game.

### 6. Custom Combo
Pick and choose which unlocks you want. Lets you mix and match any of the above options.

### 7. Set Gold
Set your gold to any amount you want.

---

## FAQ

**Will this get me banned?**
No. The Spell Brigade is PvE co-op with no anti-cheat. Saves are local.

**Can I undo it?**
Yes. The tool creates a backup folder each time. Copy the files back to restore.

**Where is my save folder?**
The tool finds it automatically. If it can't, press Win+R and paste:
```
%userprofile%\AppData\LocalLow\BoltBlasterGames\TheSpellBrigade
```

**My changes didn't work**
Make sure the game is fully closed (check system tray). If your save got reset, restore from the backup folder.

**"pycryptodome" or "Crypto" error**
Run `pip install pycryptodome`. If that fails, try `python -m pip install pycryptodome`.

**"python is not recognized"**
Reinstall Python and check "Add Python to PATH" during install.

**Steam Deck / Linux?**
Works on any OS with Python. Save path on Proton:
```
~/.steam/steam/steamapps/compatdata/[APPID]/pfx/drive_c/users/steamuser/AppData/LocalLow/BoltBlasterGames/TheSpellBrigade/
```
Run the script and paste the path when prompted.
