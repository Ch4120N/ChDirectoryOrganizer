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


# Main Class
class Ch4120N_Directory_Organizer:
    def build_parser(self):
        parser = argparse.ArgumentParser(description="ChDirectoryOrganaizer - Advanced file organizer by Ch4120N")
        subparsers = parser.add_subparsers(dest="mode")

        # --- by-date ---
        date_parser = subparsers.add_parser("by-date")
        date_parser.add_argument("directory", nargs="?")
        date_parser.add_argument("--pattern", default="%H.%M_%m.%d.%Y")
        date_parser.add_argument("--rule", choices=["earliest", "latest"], default="earliest")
        date_parser.add_argument("--action", choices=["move", "copy"], default="move")
        date_parser.add_argument("--dry-run", action="store_true")

        # --- by-type ---
        type_parser = subparsers.add_parser("by-type")
        type_parser.add_argument("directory", nargs="?")
        type_parser.add_argument("--case-sensitive", action="store_true")
        type_parser.add_argument("--action", choices=["move", "copy"], default="move")
        type_parser.add_argument("--dry-run", action="store_true")

        # --- by-size ---
        size_parser = subparsers.add_parser("by-size")
        size_parser.add_argument("directory", nargs="?")
        size_parser.add_argument("--brackets", nargs="+")
        size_parser.add_argument("--action", choices=["move", "copy"], default="move")
        size_parser.add_argument("--dry-run", action="store_true")

        # --- by-prefix ---
        prefix_parser = subparsers.add_parser("by-prefix")
        prefix_parser.add_argument("directory", nargs="?")
        prefix_parser.add_argument("--length", type=int, default=1)
        prefix_parser.add_argument("--action", choices=["move", "copy"], default="move")
        prefix_parser.add_argument("--dry-run", action="store_true")

        # --- custom ---
        custom_parser = subparsers.add_parser("custom")
        custom_parser.add_argument("directory", nargs="?")
        custom_parser.add_argument("--module", required=True)
        custom_parser.add_argument("--action", choices=["move", "copy"], default="move")
        custom_parser.add_argument("--dry-run", action="store_true")

        # --- undo ---
        undo_parser = subparsers.add_parser("undo")
        undo_parser.add_argument("directory", nargs="?")

        return parser.parse_args()
    
    def run(self, args):
        if not args.mode:
            MsgDec.info('Starting interactive mode...')
            self.interactive_mode()
            return
        
        if args.mode == "undo":
            directory = Path(args.directory) if args.directory else Path.cwd()
            FileOrganizer.undo_last(directory)
            return

        if not args.directory:
            args.directory = self.prompt("Enter directory", default=".")
        directory = Path(args.directory)

        action = getattr(args, "action", "move")
        dry_run = getattr(args, "dry_run", False)
        organizer = FileOrganizer(directory, action)

        if args.mode == "by-date":
            organizer.organize_by_date(date_pattern=args.pattern, time_rule=args.rule, dry_run=dry_run)
        elif args.mode == "by-type":
            organizer.organize_by_type(case_sensitive=args.case_sensitive, dry_run=dry_run)
        elif args.mode == "by-size":
            brackets = self.parse_brackets(args.brackets)
            organizer.organize_by_size(brackets, dry_run)
        elif args.mode == "by-prefix":
            organizer.organize_by_prefix(length=args.length, dry_run=dry_run)
        elif args.mode == "custom":
            import importlib.util
            spec = importlib.util.spec_from_file_location("custom_organize", args.module)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if not hasattr(mod, "map_file"):
                MsgDec.error("Custom module must define a `map_file` function")
                sys.exit(1)
            organizer.organize_custom(mod.map_file, dry_run)
    
    def interactive_mode(self):
        modes = ["by-date", "by-type", "by-size", "by-prefix", "custom", "undo"]

        MsgDec.info("Available modes")
        for i, m in enumerate(modes, 1):
            print(f"  {i}) {m}")
        choice = self.prompt("Choose organization mode").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(modes):
            mode = modes[int(choice)-1]
        else:
            mode = choice
        if mode not in modes:
            MsgDec.error(f"Invalid mode '{mode}'")
            sys.exit(1)

        if mode == "undo":
            directory = self.prompt("Directory to undo", default=".")
            FileOrganizer.undo_last(Path(directory))
            return

        directory = self.prompt("Target directory", default=".")
        action = "move" if self.confirm("Move files? (otherwise copy)", default=True) else "copy"
        dry_run = self.confirm("Perform a dry run first?", default=False)
        organizer = FileOrganizer(Path(directory), action)

        if mode == "by-date":
            pattern = self.prompt(f"Folder name pattern {Color.Green}({Color.Red}strftime, {Color.White}e,g. {Color.Blue}%H.%M_%m.%d.%Y{Color.Green}){Color.White}? ", default="%H.%M_%m.%d.%Y")
            rule = "earliest"
            if self.confirm("Use latest time instead of earliest?", default=False):
                rule = "latest"
            organizer.organize_by_date(date_pattern=pattern, time_rule=rule, dry_run=dry_run)

        elif mode == "by-type":
            case_sensitive = self.confirm("Case-sensitive extensions?", default=False)
            organizer.organize_by_type(case_sensitive=case_sensitive, dry_run=dry_run)

        elif mode == "by-size":
            brackets = [(0, 1024**2, "small"), (1024**2, 10*1024**2, "medium"), (10*1024**2, None, "large")]
            organizer.organize_by_size(brackets, dry_run)

        elif mode == "by-prefix":
            length = int(self.prompt("Number of prefix characters", default="1"))
            organizer.organize_by_prefix(length=length, dry_run=dry_run)

        elif mode == "custom":
            module_path = self.prompt("Path to custom .py file (must contain map_file function)")
            import importlib.util
            spec = importlib.util.spec_from_file_location("custom_organize", module_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            organizer.organize_custom(mod.map_file, dry_run)

    def colored_prompt(self, *args):
        prompt_str = ' '.join(str(arg) for arg in args)
        print(prompt_str, end='', flush=True)
        try:
            return input()
        except (KeyboardInterrupt, EOFError):
            print('\n')
            MsgDec.error('Program Terminated!')
            sys.exit(1)

    def prompt(self, message: str, default=None):
        text = MsgDec.prompt(message)

        if default:
            return self.colored_prompt(f"{text} {Color.Green}[{Color.White}{default}{Color.Green}]{Color.White}? ") or default
        return self.colored_prompt(f"{text}{Color.White}? ")

    def confirm(self, message: str, default=True):
        text = MsgDec.prompt(message)

        yes = "Y/n" if default else "y/N"
        ans = self.colored_prompt(f"{text} {Color.Green}({Color.Aqua}{yes}{Color.Green}){Color.White}? ").strip().lower()
        if not ans:
            return default
        return ans in ("y", "yes")

    def parse_brackets(self, brackets_str):
        if not brackets_str:
            return [
                (0, 1024**2, "small"),
                (1024**2, 10 * 1024**2, "medium"),
                (10 * 1024**2, None, "large"),
            ]
        brackets = []
        for part in brackets_str:
            range_str, name = part.split(":")
            if "-" in range_str:
                low_str, high_str = range_str.split("-")
                low = int(low_str) if low_str else None
                high = int(high_str) if high_str else None
            else:
                low = high = int(range_str)
            brackets.append((low, high, name))
        return brackets



if __name__ == "__main__":
    app = Ch4120N_Directory_Organizer()
    args = app.build_parser()
    app.run(args)