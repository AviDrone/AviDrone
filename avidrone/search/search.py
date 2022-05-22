#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    AVIDRONE SEARCH
"""
from __future__ import print_function

import argparse
import asyncio
import datetime
import logging
import math
import time

from dronekit import (
    Command,
    LocationGlobal,
    LocationGlobalRelative,
    VehicleMode,
    connect,
)

# import primary
# import secondary

# import util


# log
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler = logging.FileHandler("search.log")
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

print("main test")  # TODO remove after testing
def search():
    log.info("--- BEGIN SEARCH ---")


if __name__ == "__main__":
    search()
