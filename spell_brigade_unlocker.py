"""
The Spell Brigade - Save Unlocker
Unlock covenants, complete challenges, set prestige, and more.

Requirements: pip install pycryptodome
"""
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad, pad
from Crypto.Hash import SHA1
import gzip, re, os, shutil, sys
from datetime import datetime

PASSWORD = "vhp*UCETJFwjE*8B!EPE"
DEFAULT_SAVE_DIR = os.path.join(
    os.environ.get("USERPROFILE", ""),
    r"AppData\LocalLow\BoltBlasterGames\TheSpellBrigade"
)

ALL_CHALLENGE_IDS = list(range(149))
ALL_OLD_CHALLENGE_IDS = list(range(1, 106))
ALL_ELEMENT_IDS = list(range(21))
ALL_OBJECTIVES = list(range(11))
ALL_ARTIFACTS = [1, 3, 5, 6, 7, 8, 9, 13, 15, 16, 17, 19, 20]
ALL_UPGRADE_IDS = list(range(20))
MAX_NEW_UPGRADE_LEVEL = 6
MAX_OLD_UPGRADE_LEVEL = 4

CHALLENGE_TARGET_VALUES = {
    5: 8000, 6: 3000000, 7: 800000, 8: 12000, 9: 15000,
    10: 21, 11: 5, 14: 5, 15: 8, 16: 7, 17: 14,
    18: 11, 19: 5, 20: 12, 21: 25, 22: 40,
    23: 2100, 26: 9100, 29: 35, 31: 450, 32: 38,
    37: 1500, 38: 315000, 53: 300, 54: 410, 56: 13, 57: 12,
    58: 1100, 59: 90, 106: 50, 107: 440, 110: 3, 111: 8,
    112: 12, 115: 10, 116: 5, 117: 900, 121: 100,
    128: 850, 131: 13000, 132: 4, 133: 4, 134: 4,
}

CHAR_NAMES = {
    0: "Reginald", 1: "MoonMage", 2: "SunMage (Aldric)", 3: "KeyMage (Kavin)",
    4: "Ludwig", 5: "Campanelli", 6: "Hatty", 7: "WizardKing (Balthazar)",
    8: "StarMage", 9: "Smithy", 10: "BirdMage (Maggie)", 11: "PlantMage (Bryony)",
    12: "FluteMage (Pipwick)", 13: "VampireMage", 14: "BellMage (Knelly)"
}


def decrypt_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    salt = data[:16]
    key = PBKDF2(PASSWORD, salt, dkLen=16, count=100, hmac_hash_module=SHA1)
    cipher = AES.new(key, AES.MODE_CBC, IV=salt)
    decrypted = unpad(cipher.decrypt(data[16:]), AES.block_size)
    return gzip.decompress(decrypted), salt


def encrypt_file(text_bytes, salt, output_path):
    compressed = gzip.compress(text_bytes)
    key = PBKDF2(PASSWORD, salt, dkLen=16, count=100, hmac_hash_module=SHA1)
    cipher = AES.new(key, AES.MODE_CBC, IV=salt)
    encrypted = salt + cipher.encrypt(pad(compressed, AES.block_size))
    with open(output_path, 'wb') as f:
        f.write(encrypted)


def find_save_dir():
    if os.path.isdir(DEFAULT_SAVE_DIR):
        return DEFAULT_SAVE_DIR

    save_subpath = r"AppData\LocalLow\BoltBlasterGames\TheSpellBrigade"
    userprofile = os.environ.get("USERPROFILE", "")

    for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        candidates = [
            os.path.join(f"{drive}:\\", "Users"),
        ]
        for users_dir in candidates:
            if not os.path.isdir(users_dir):
                continue
            try:
                for user_folder in os.listdir(users_dir):
                    candidate = os.path.join(users_dir, user_folder, save_subpath)
                    if os.path.isdir(candidate):
                        return candidate
            except PermissionError:
                continue

    return None


def backup_saves(save_dir):
    backup_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"save_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(backup_dir, exist_ok=True)
    for fname in os.listdir(save_dir):
        if fname.startswith('save_'):
            shutil.copy2(os.path.join(save_dir, fname), os.path.join(backup_dir, fname))
    return backup_dir


def get_current_state(save_dir):
    slots = sorted([f for f in os.listdir(save_dir) if f.startswith('save_slot_')])
    raw, _ = decrypt_file(os.path.join(save_dir, slots[0]))
    text = raw.decode('utf-8')

    chars = {}
    rp_start = text.find('"RankProgressPerCharacter"')
    rp_dict_start = text.find('{', rp_start + 25)
    depth = 0
    rp_dict_end = rp_dict_start
    for j in range(rp_dict_start, len(text)):
        if text[j] == '{':
            depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0:
                rp_dict_end = j
                break
    section = text[rp_dict_start:rp_dict_end + 1]

    for cid in range(15):
        pattern = rf'{cid}:\{{[^}}]*?"CurrentRank" : (\d+)[^}}]*?"ProgressTowardsNextRank" : ([0-9.]+)[^}}]*?"Prestige" : (\d+)'
        m = re.search(pattern, section, re.DOTALL)
        if m:
            chars[cid] = {
                'rank': int(m.group(1)),
                'progress': m.group(2),
                'prestige': int(m.group(3))
            }

    ch_start = text.find('"New_ProgressForChallenges"')
    challenges = {}
    entries = re.findall(r'(\d+):\{\s*"Value"\s*:\s*(\d+),\s*"IsCompleted"\s*:\s*(true|false)\s*\}', text[ch_start:])
    for cid, val, completed in entries:
        challenges[int(cid)] = {'value': int(val), 'completed': completed == 'true'}

    ie_start = text.find('"InfusedElements"')
    ie_end = text.find(']', ie_start)
    infused = set()
    if ie_start >= 0:
        elements = re.findall(r'\d+', text[ie_start:ie_end])
        infused = set(int(x) for x in elements)

    gold_m = re.search(r'"Gold" : (\d+)', text)
    gold = int(gold_m.group(1)) if gold_m else 0

    upgrades = {}
    up_start = text.find('"New_LevelForUpgrades"')
    if up_start >= 0:
        up_brace = text.find('{', up_start)
        up_end = text.find('}', up_brace)
        for m in re.finditer(r'(\d+):(\d+)', text[up_brace:up_end]):
            upgrades[int(m.group(1))] = int(m.group(2))

    return chars, challenges, infused, gold, upgrades


def set_gold(text, amount):
    return re.sub(r'"Gold" : \d+', f'"Gold" : {amount}', text)


def clear_reset_flag(text):
    return text.replace('"HasClearedSaveData" : true', '"HasClearedSaveData" : false')


def set_prestige(text, prestige_level):
    text = ensure_characters_exist(text)
    return re.sub(r'"Prestige" : \d+', f'"Prestige" : {prestige_level}', text)


def set_ascend_ready(text):
    text = ensure_characters_exist(text)
    text = re.sub(r'"CurrentRank" : \d+', '"CurrentRank" : 10', text)
    text = re.sub(r'"ProgressTowardsNextRank" : [0-9.]+', '"ProgressTowardsNextRank" : 0', text)
    return text


def ensure_characters_exist(text):
    rp_start = text.find('"RankProgressPerCharacter"')
    if rp_start < 0:
        return text
    brace_start = text.find('{', rp_start + 25)
    brace_end = text.find('}', brace_start + 1)
    content = text[brace_start + 1:brace_end].strip()
    if content:
        return text
    indent = '\t\t\t\t'
    inner = indent + '\t'
    entries = []
    for cid in range(15):
        entries.append(
            f'{indent}{cid}:{{\r\n'
            f'{inner}"CurrentRank" : 1,\r\n'
            f'{inner}"ProgressTowardsNextRank" : 0,\r\n'
            f'{inner}"Prestige" : 0\r\n'
            f'{indent}}}'
        )
    new_content = '{\r\n' + ',\r\n'.join(entries) + '\r\n\t\t\t}'
    text = text[:brace_start] + new_content + text[brace_end + 1:]
    return text


def add_all_infusions(text):
    all_elements_str = ','.join(str(e) for e in ALL_ELEMENT_IDS)
    new_list = '\r\n\t\t\t\t' + all_elements_str + '\r\n\t\t\t'
    return re.sub(r'("InfusedElements" : \[)[^\]]*(\])', r'\g<1>' + new_list + r'\2', text)


def max_upgrades(text):
    new_entries = ','.join(f'{uid}:{MAX_NEW_UPGRADE_LEVEL}' for uid in ALL_UPGRADE_IDS)
    text = re.sub(
        r'("New_LevelForUpgrades" : \{)[^}]*(\})',
        r'\g<1>' + new_entries + r'\r\n\t\t\t\2',
        text
    )
    old_entries = ','.join(f'{uid}:{MAX_OLD_UPGRADE_LEVEL}' for uid in ALL_UPGRADE_IDS)
    text = re.sub(
        r'("LevelForUpgrades" : \{)[^}]*(\})',
        r'\g<1>' + old_entries + r'\r\n\t\t\t\2',
        text
    )
    return text


def set_total_artifacts(text):
    return re.sub(r'"TotalCollectedArtifacts" : \d+', '"TotalCollectedArtifacts" : 45', text)


def complete_old_challenges(text):
    ch_start = text.find('"ProgressForChallenges"')
    if ch_start < 0:
        return text

    new_ch_start = text.find('"New_ProgressForChallenges"')
    old_section_end = new_ch_start if new_ch_start > ch_start else len(text)
    old_section = text[ch_start:old_section_end]

    existing_ids = set(int(m.group(1)) for m in re.finditer(r'(\d+):\{', old_section))

    for cid in ALL_OLD_CHALLENGE_IDS:
        if cid in existing_ids:
            pattern = rf'(?<!\d)({cid}:\{{[^}}]*?"IsCompleted" : )false'
            text = re.sub(pattern, r'\g<1>true', text, count=1)

    missing_ids = set(ALL_OLD_CHALLENGE_IDS) - existing_ids
    if missing_ids:
        indent = '\t\t\t\t\t'
        indent_m = re.search(r'\n(\t+)\d+:\{', old_section)
        if indent_m:
            indent = indent_m.group(1)
        inner = indent + '\t'

        last_entry = None
        for m in re.finditer(r'\d+:\{[^}]*?\}', old_section, re.DOTALL):
            last_entry = m

        if last_entry:
            insert_pos = ch_start + last_entry.end()
            new_entries = ''
            for cid in sorted(missing_ids):
                new_entries += f',\r\n{indent}{cid}:{{\r\n{inner}"Value" : 1,\r\n{inner}"IsCompleted" : true\r\n{indent}}}'
            text = text[:insert_pos] + new_entries + text[insert_pos:]
        else:
            brace_start = text.find('{', ch_start + 22)
            new_entries = ''
            for i, cid in enumerate(sorted(missing_ids)):
                sep = '' if i == 0 else ','
                new_entries += f'{sep}\r\n{indent}{cid}:{{\r\n{inner}"Value" : 1,\r\n{inner}"IsCompleted" : true\r\n{indent}}}'
            text = text[:brace_start + 1] + new_entries + '\r\n\t\t\t\t' + text[brace_start + 1:]

    return text


def complete_world_difficulties(text):
    all_worlds = '0:[\r\n\t\t\t\t\t0,1,2\r\n\t\t\t\t],1:[\r\n\t\t\t\t\t0,1,2\r\n\t\t\t\t],2:[\r\n\t\t\t\t\t0,1,2\r\n\t\t\t\t],3:[\r\n\t\t\t\t\t0,1,2\r\n\t\t\t\t]'
    pattern = r'("CompletedDifficultiesPerWorld" : \{)[^}]*(?:\[[^\]]*\][^}]*)*(\})'
    start = text.find('"CompletedDifficultiesPerWorld"')
    if start < 0:
        return text
    brace_start = text.find('{', start + 30)
    depth = 0
    brace_end = brace_start
    for j in range(brace_start, len(text)):
        if text[j] == '{' or text[j] == '[':
            depth += 1
        elif text[j] == '}' or text[j] == ']':
            depth -= 1
            if depth == 0:
                brace_end = j
                break
    text = text[:brace_start] + '{' + all_worlds + '}' + text[brace_end + 1:]
    return text


def complete_objectives(text):
    all_obj = ','.join(str(o) for o in ALL_OBJECTIVES)
    new_list = '\r\n\t\t\t\t' + all_obj + '\r\n\t\t\t'
    return re.sub(r'("CompletedObjectives" : \[)[^\]]*(\])', r'\g<1>' + new_list + r'\2', text)


def complete_artifacts(text):
    all_art = ','.join(str(a) for a in ALL_ARTIFACTS)
    new_list = '\r\n\t\t\t\t' + all_art + '\r\n\t\t\t'
    return re.sub(r'("CollectedArtifacts" : \[)[^\]]*(\])', r'\g<1>' + new_list + r'\2', text)


def complete_all_challenges(text):
    ch_start = text.find('"New_ProgressForChallenges"')
    if ch_start < 0:
        return text

    before = text[:ch_start]
    section = text[ch_start:]

    brace_pos = section.find('{')
    depth = 0
    dict_end = brace_pos
    for j in range(brace_pos, len(section)):
        if section[j] == '{':
            depth += 1
        elif section[j] == '}':
            depth -= 1
            if depth == 0:
                dict_end = j
                break
    ch_dict = section[brace_pos:dict_end + 1]

    existing_ids = set(int(m.group(1)) for m in re.finditer(r'(\d+):\{', ch_dict))

    for cid in ALL_CHALLENGE_IDS:
        if cid in existing_ids:
            pattern = rf'(?<!\d)({cid}:\{{[^}}]*?"IsCompleted" : )false'
            section = re.sub(pattern, r'\g<1>true', section, count=1)

            if cid in CHALLENGE_TARGET_VALUES:
                target = CHALLENGE_TARGET_VALUES[cid]
                pattern_val = rf'(?<!\d)({cid}:\{{[^}}]*?"Value" : )\d+'
                section = re.sub(pattern_val, rf'\g<1>{target}', section, count=1)

    missing_ids = set(ALL_CHALLENGE_IDS) - existing_ids
    if missing_ids:
        indent = '\t\t\t\t'
        indent_m = re.search(r'\n(\t+)\d+:\{', ch_dict)
        if indent_m:
            indent = indent_m.group(1)
        inner = indent + '\t'

        last_entry = None
        for m in re.finditer(r'\d+:\{[^}]*?\}', ch_dict, re.DOTALL):
            last_entry = m

        if last_entry:
            insert_pos = brace_pos + last_entry.end()
            new_entries = ''
            for cid in sorted(missing_ids):
                val = CHALLENGE_TARGET_VALUES.get(cid, 1)
                new_entries += f',\r\n{indent}{cid}:{{\r\n{inner}"Value" : {val},\r\n{inner}"IsCompleted" : true\r\n{indent}}}'
            section = section[:insert_pos] + new_entries + section[insert_pos:]
        else:
            new_entries = ''
            for i, cid in enumerate(sorted(missing_ids)):
                val = CHALLENGE_TARGET_VALUES.get(cid, 1)
                sep = '' if i == 0 else ','
                new_entries += f'{sep}\r\n{indent}{cid}:{{\r\n{inner}"Value" : {val},\r\n{inner}"IsCompleted" : true\r\n{indent}}}'
            section = section[:brace_pos + 1] + new_entries + '\r\n\t\t\t' + section[brace_pos + 1:]

    return before + section


def process_slots(save_dir, operations):
    slots = sorted([f for f in os.listdir(save_dir) if f.startswith('save_slot_')])
    for slot_name in slots:
        slot_path = os.path.join(save_dir, slot_name)
        raw, salt = decrypt_file(slot_path)
        text = raw.decode('utf-8')

        for op in operations:
            text = op(text)

        encrypt_file(text.encode('utf-8'), salt, slot_path)
        print(f"  {slot_name}: done")


def show_status(save_dir):
    chars, challenges, infused, gold, upgrades = get_current_state(save_dir)

    print(f"\n  GOLD: {gold:,}")

    print("\n  CHARACTERS:")
    for cid in range(15):
        if cid in chars:
            c = chars[cid]
            name = CHAR_NAMES.get(cid, f"Unknown_{cid}")
            ascend = "ASCEND READY" if c['rank'] >= 10 else f"Rank {c['rank']}"
            print(f"    {name:30s} Prestige={c['prestige']:3d}  {ascend}")

    completed = sum(1 for c in challenges.values() if c['completed'])
    total = len(ALL_CHALLENGE_IDS)
    existing = len(challenges)
    print(f"\n  CHALLENGES: {completed}/{existing} completed ({total - existing} missing from save)")

    print(f"  INFUSIONS:  {len(infused)}/{len(ALL_ELEMENT_IDS)} elements discovered")

    maxed = sum(1 for v in upgrades.values() if v >= MAX_NEW_UPGRADE_LEVEL)
    print(f"  UPGRADES:   {maxed}/{len(ALL_UPGRADE_IDS)} maxed (level {MAX_NEW_UPGRADE_LEVEL})")


def main():
    print("=" * 60)
    print("  THE SPELL BRIGADE - SAVE UNLOCKER")
    print("  Unlock covenants, challenges, infusions & more")
    print("=" * 60)

    save_dir = find_save_dir()
    if not save_dir:
        print(f"\n  Save directory not found automatically.")
        print(f"  Checked: {DEFAULT_SAVE_DIR}")
        print(f"\n  The save folder is usually at:")
        print(f"  C:\\Users\\YourName\\AppData\\LocalLow\\BoltBlasterGames\\TheSpellBrigade")
        print(f"\n  To find it: press Win+R, paste this and hit Enter:")
        print(f"  %userprofile%\\AppData\\LocalLow\\BoltBlasterGames\\TheSpellBrigade")
        print()
        save_dir = input("  Paste your save folder path here: ").strip().strip('"')
        if not os.path.isdir(save_dir):
            print(f"\n  Folder not found: {save_dir}")
            print("  Make sure the game has been played at least once.")
            input("\n  Press Enter to exit...")
            return

    save_slots = [f for f in os.listdir(save_dir) if f.startswith('save_slot_')]
    if not save_slots:
        print(f"\n  No save files found in: {save_dir}")
        print("\n  Files in this folder:")
        try:
            files = os.listdir(save_dir)
            if files:
                for f in files:
                    size = os.path.getsize(os.path.join(save_dir, f))
                    print(f"    {f} ({size} bytes)")
            else:
                print("    (empty folder)")
        except Exception:
            print("    (could not list files)")
        print("\n  Play the game at least once, then close it and try again.")
        input("\n  Press Enter to exit...")
        return
    print(f"  Found {len(save_slots)} save slots: {', '.join(sorted(save_slots))}")

    print(f"\n  Save directory: {save_dir}")
    print("\n  Loading current save state...")

    try:
        show_status(save_dir)
    except Exception as e:
        print(f"\n  Error reading save: {e}")
        return

    print("\n" + "-" * 60)
    print("  OPTIONS:")
    print("    1. UNLOCK ALL (recommended)")
    print("       - Complete all quests (all 7 tabs)")
    print("       - All worlds/difficulties/objectives completed")
    print("       - Collect all artifacts")
    print("       - Add all infusion elements")
    print("       - Max all upgrades")
    print("       - Set gold to 9,999,999")
    print("       - Set all characters to Prestige 2 + ascend-ready")
    print("       - Covenants unlock at P2 via in-game ascension")
    print()
    print("    2. Set custom prestige level + ascend-ready")
    print("       - Choose your prestige level for all characters")
    print()
    print("    3. Complete all challenges only")
    print("       - Marks all quests/achievements as completed")
    print("       - Adds missing challenge entries")
    print()
    print("    4. Add all infusions only")
    print("       - Discovers all 21 element infusions")
    print()
    print("    5. Set ascend-ready only")
    print("       - Sets Rank=10, Progress=0 (keeps prestige)")
    print()
    print("    6. Custom combo")
    print("       - Pick what you want")
    print()
    print("    7. Set gold")
    print("       - Set your gold to any amount")
    print()
    print("    0. Exit")
    print("-" * 60)

    choice = input("\n  Enter choice (0-7): ").strip()

    if choice == '0':
        print("  Exiting.")
        return

    operations = []

    if choice == '1':
        operations = [
            clear_reset_flag,
            lambda t: set_prestige(t, 2),
            set_ascend_ready,
            complete_old_challenges,
            complete_all_challenges,
            add_all_infusions,
            complete_world_difficulties,
            complete_objectives,
            complete_artifacts,
            max_upgrades,
            set_total_artifacts,
            lambda t: set_gold(t, 9999999),
        ]
        desc = "UNLOCK ALL"

    elif choice == '2':
        try:
            level = int(input("  Enter prestige level (0-999): ").strip())
        except ValueError:
            print("  Invalid number. Exiting.")
            return
        operations = [
            lambda t, p=level: set_prestige(t, p),
            set_ascend_ready,
        ]
        desc = f"Set Prestige {level} + ascend-ready"

    elif choice == '3':
        operations = [complete_all_challenges]
        desc = "Complete all challenges"

    elif choice == '4':
        operations = [add_all_infusions]
        desc = "Add all infusions"

    elif choice == '5':
        operations = [set_ascend_ready]
        desc = "Set ascend-ready"

    elif choice == '6':
        print("\n  Select what to apply (y/n for each):")
        if input("    Complete all challenges? (y/n): ").strip().lower() == 'y':
            operations.append(complete_all_challenges)
        if input("    Add all infusions? (y/n): ").strip().lower() == 'y':
            operations.append(add_all_infusions)
        if input("    Set ascend-ready? (y/n): ").strip().lower() == 'y':
            operations.append(set_ascend_ready)
        set_p = input("    Set prestige? (enter number or 'n' to skip): ").strip()
        if set_p.lower() != 'n':
            try:
                level = int(set_p)
                operations.append(lambda t, p=level: set_prestige(t, p))
            except ValueError:
                print("    Invalid number, skipping prestige.")
        set_g = input("    Set gold? (enter amount or 'n' to skip): ").strip()
        if set_g.lower() != 'n':
            try:
                amount = int(set_g.replace(',', ''))
                operations.append(lambda t, g=amount: set_gold(t, g))
            except ValueError:
                print("    Invalid number, skipping gold.")
        if not operations:
            print("  Nothing selected. Exiting.")
            return
        desc = "Custom combo"

    elif choice == '7':
        try:
            amount = int(input("  Enter gold amount: ").strip().replace(',', ''))
        except ValueError:
            print("  Invalid number. Exiting.")
            return
        operations = [lambda t, g=amount: set_gold(t, g)]
        desc = f"Set gold to {amount:,}"

    else:
        print("  Invalid choice.")
        input("\n  Press Enter to exit...")
        return

    print(f"\n  Action: {desc}")
    print("  IMPORTANT: Make sure the game is FULLY CLOSED!")
    confirm = input("  Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("  Cancelled.")
        return

    backup_dir = backup_saves(save_dir)
    print(f"\n  Backup saved to: {backup_dir}")

    print("\n  Applying changes...")
    try:
        process_slots(save_dir, operations)
    except Exception as e:
        print(f"\n  ERROR: {e}")
        print("  Restoring backup...")
        for fname in os.listdir(backup_dir):
            shutil.copy2(os.path.join(backup_dir, fname), os.path.join(save_dir, fname))
        print("  Backup restored. No changes made.")
        return

    print("\n  Verifying...")
    try:
        show_status(save_dir)
    except Exception as e:
        print(f"  Verification error: {e}")

    print(f"\n  Done! Backup at: {backup_dir}")
    print("  Launch the game to see your changes.")
    print("\n  NOTE: Characters are set to ascend-ready (Rank 10).")
    print("  Ascend them manually in-game to unlock covenants (need P2).")
    print("  Steam achievements will sync automatically on game load.")

    input("\n  Press Enter to exit...")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n  UNEXPECTED ERROR: {e}")
        print("  Please report this error.")
        input("\n  Press Enter to exit...")
