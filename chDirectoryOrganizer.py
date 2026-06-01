#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  ____  _____  _    _  ____  ____  ____  ____     ____  _  _     ___  _   _  __  __  ___   ___  _  _ 
# (  _ \(  _  )( \/\/ )( ___)(  _ \( ___)(  _ \   (  _ \( \/ )   / __)( )_( )/. |/  )(__ \ / _ \( \( )
#  )___/ )(_)(  )    (  )__)  )   / )__)  )(_) )   ) _ < \  /   ( (__  ) _ ((_  _))(  / _/( (_) ))  ( 
# (__)  (_____)(__/\__)(____)(_)\_)(____)(____/   (____/ (__)    \___)(_) (_) (_)(__)(____)\___/(_)\_)
######################################################################################################

"""
ChFolderOrganaizer - Advanced cross-platform directory organizer.
Owner   : Ch4120N
GitHub  : GitHub.COM/Ch4120N
Telegram: T.ME/Ch4120N
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Tuple

# Optional dependencies

try:
    from colorama import Fore, init
    init(autoreset=True)

    FORCED_COLORED = True
except ImportError:
    FORCED_COLORED = False


try:
    from tqdm import tqdm
    PROGRESS_AVAILABLE = True
except ImportError:
    PROGRESS_AVAILABLE = False




# Color Class
class Color:
    if FORCED_COLORED:
        Aqua       = Fore.LIGHTCYAN_EX
        Green      = Fore.LIGHTGREEN_EX
        Red        = Fore.LIGHTRED_EX
        Blue       = Fore.LIGHTBLUE_EX
        Yellow     = Fore.LIGHTYELLOW_EX
        Orange     = Fore.YELLOW
        Purple     = Fore.LIGHTMAGENTA_EX
        White      = Fore.LIGHTWHITE_EX
        Reset      = Fore.RESET
    else:
        Aqua       = ''
        Green      = ''
        Red        = ''
        Blue       = ''
        Yellow     = ''
        Purple     = ''
        White      = ''
        Reset      = ''

class MessageDecorators:
    def info(self, RequestMessage: str):
        sys.stdout.write(Color.Aqua + '[ ' + Color.White + '*' + Color.Aqua + ' ] '  + Color.White + RequestMessage + '\n' + Color.Reset)
        sys.stdout.flush()
    
    def success(self, RequestMessage: str):
        sys.stdout.write(Color.Green + '[ ' + Color.White + '+' + Color.Green + ' ] '  + Color.White + RequestMessage + '\n' + Color.Reset)
        sys.stdout.flush()
    
    def error(self, RequestMessage: str):
        sys.stdout.write(Color.Red + '[ ' + Color.White + '-' + Color.Red + ' ] '  + Color.White + RequestMessage + '\n' + Color.Reset)
        sys.stdout.flush()

    def warning(self, RequestMessage: str):
        sys.stdout.write(Color.Orange + '[ ' + Color.White + '!' + Color.Orange + ' ] '  + Color.White + RequestMessage + '\n' + Color.Reset)
        sys.stdout.flush()
    
    def progress(self, RequestMessage: str):
        sys.stdout.write(Color.White + '[ ' + Color.Aqua + '#' + Color.White + ' ] ' + RequestMessage + '\n' + Color.Reset)
        sys.stdout.flush()
    
    def prompt(self, RequestMessage: str):
        return (Color.Purple + '[ ' + Color.White + '?' + Color.Purple + ' ] ' + Color.White + RequestMessage)

# Requried Variables
MsgDec = MessageDecorators()
MANIFEST_FILE = ".ChDirectoryOrganizer_Manifest.json"

# Core organizer

class FileOrganizer:
    """Organize files with multiple strategies."""

    def __init__(self, directory: Path, action: str = "move"):
        self.directory = directory.resolve()
        if not self.directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.directory}")
        self.action = action.lower()  # "move" or "copy"
        self.manifest: List[Dict[str, str]] = []

    def scan_files(self) -> List[Path]:
        MsgDec.info("Scanning files...")
        files = [f for f in self.directory.iterdir() if f.is_file()]
        MsgDec.info(f"Found {len(files)} file(s)")
        return files

    def _process_files(self, mapping: Dict[Path, Path], dry_run: bool = False):
        files = list(mapping.keys())
        if PROGRESS_AVAILABLE:
            files = tqdm(files, desc="Processing", unit="file",
                         bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}")
        for src in files:
            dest = mapping[src]
            if dry_run:
                MsgDec.progress(f"{src.name} -> {dest.relative_to(self.directory)}")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                if self.action == "move":
                    src.rename(dest)
                else:
                    shutil.copy2(src, dest)
                MsgDec.info(f"{self.action.capitalize()}d: {src.name} -> {dest.relative_to(self.directory)}")
                self.manifest.append({"old": str(src), "new": str(dest)})
            except OSError as e:
                MsgDec.error(f"Failed to {self.action} {src.name}: {e}")

    def save_manifest(self):
        if self.manifest:
            with open(self.directory / MANIFEST_FILE, "w") as f:
                json.dump(self.manifest, f, indent=2)
            MsgDec.info(f"Manifest saved ({len(self.manifest)} entries)")

    @staticmethod
    def undo_last(directory: Path):
        manifest_path = directory / MANIFEST_FILE
        if not manifest_path.exists():
            MsgDec.warning("No manifest found - nothing to undo.")
            return
        with open(manifest_path) as f:
            entries = json.load(f)
        MsgDec.info(f"Undoing {len(entries)} operations...")
        for entry in reversed(entries):
            old = Path(entry["old"])
            new = Path(entry["new"])
            if new.exists():
                if old.exists():
                    MsgDec.warning(f"Both {old} and {new} exist - skipping undo")
                    continue
                new.rename(old)
                MsgDec.info(f"Restored: {old.name}")
            else:
                MsgDec.warning(f"{new} no longer exists - cannot undo")
        manifest_path.unlink()
        MsgDec.info("Undo complete.")

    # ============ Organization strategies ============
    def organize_by_date(self, date_pattern: str = "%H.%M_%m.%d.%Y",
                         time_rule: str = "earliest", dry_run: bool = False):
        files = self.scan_files()
        if not files:
            MsgDec.warning("No files found.")
            return
        date_map = {}
        for f in files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            d = mtime.date()
            if d not in date_map:
                date_map[d] = (None, [])
            extreme_dt, f_list = date_map[d]
            if extreme_dt is None:
                extreme_dt = mtime
            else:
                if time_rule == "earliest":
                    extreme_dt = min(extreme_dt, mtime)
                else:
                    extreme_dt = max(extreme_dt, mtime)
            f_list.append(f)
            date_map[d] = (extreme_dt, f_list)

        mapping = {}
        for d, (rep_dt, f_list) in date_map.items():
            folder_name = rep_dt.strftime(date_pattern)
            dest_folder = self.directory / folder_name
            for f in f_list:
                mapping[f] = dest_folder / f.name

        MsgDec.info(f"Grouping by date, rule={time_rule}, pattern='{date_pattern}'")
        self._process_files(mapping, dry_run=dry_run)
        if not dry_run:
            self.save_manifest()

    def organize_by_type(self, case_sensitive: bool = False, dry_run: bool = False):
        files = self.scan_files()
        mapping = {}
        for f in files:
            ext = f.suffix.lstrip(".")
            if not case_sensitive:
                ext = ext.lower()
            if not ext:
                ext = "no_extension"
            dest_folder = self.directory / ext
            mapping[f] = dest_folder / f.name
        MsgDec.info(f"Grouping by type (case-sensitive={case_sensitive})")
        self._process_files(mapping, dry_run=dry_run)
        if not dry_run:
            self.save_manifest()

    def organize_by_size(self, brackets: List[Tuple[int, int, str]], dry_run: bool = False):
        files = self.scan_files()
        mapping = {}
        for f in files:
            size = f.stat().st_size
            category = "other"
            for min_s, max_s, name in brackets:
                if min_s is not None and size < min_s:
                    continue
                if max_s is not None and size > max_s:
                    continue
                category = name
                break
            dest_folder = self.directory / category
            mapping[f] = dest_folder / f.name
        MsgDec.info(f"Grouping by size ({len(brackets)} categories)")
        self._process_files(mapping, dry_run=dry_run)
        if not dry_run:
            self.save_manifest()

    def organize_by_prefix(self, length: int = 1, dry_run: bool = False):
        files = self.scan_files()
        mapping = {}
        for f in files:
            prefix = f.stem[:length]
            if not prefix:
                prefix = "_"
            dest_folder = self.directory / prefix
            mapping[f] = dest_folder / f.name
        MsgDec.info(f"Grouping by prefix (length={length})")
        self._process_files(mapping, dry_run=dry_run)
        if not dry_run:
            self.save_manifest()

    def organize_custom(self, func_module: Callable[[Path], Path], dry_run: bool = False):
        files = self.scan_files()
        mapping = {}
        for f in files:
            dest = func_module(f)
            if dest is None:
                continue
            if not dest.is_absolute():
                dest = self.directory / dest
            mapping[f] = dest
        MsgDec.info("Using custom organization function")
        self._process_files(mapping, dry_run=dry_run)
        if not dry_run:
            self.save_manifest()
