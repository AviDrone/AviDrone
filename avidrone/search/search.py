#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import asyncio
import datetime
import logging as log
import math
import time

import default_parameters as default
import primary_search as primary_search
import secondary
from dronekit import (
    Command,
    LocationGlobal,
    LocationGlobalRelative,
    VehicleMode,
    connect,
)


def run():
    log.info(f"-- default size: {default.DEGREES}")
    log.info(f"-- default altitude: {default.ALTITUDE}")
    log.info(f"-- default land threshold: {default.LAND_THRESHOLD} \n")

    secondary.run()


if __name__ == "__main__":
    run()
