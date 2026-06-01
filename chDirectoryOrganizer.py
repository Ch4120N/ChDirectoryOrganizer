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

