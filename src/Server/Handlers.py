from flask import Flask, request, jsonify, Response, send_file
from typing import List
import os
from analysis.config import debug
from db.Services import *
import toml

FIRMWARE_CONF:str = "firmware_cfg.toml"


def mac_filter(mac:str) -> bool:
    return not DeviceService.exists(mac)

def pad_array(padding:int, arr:List[str]):
    new_arr = ["0"]*padding
    for item in arr: new_arr.append(item)

def load_config() -> dict[str, str]:
    """
    Attempt to load the database config file.
    """
    data = load_toml(FIRMWARE_CONF)
    out = data.get('firmware')
    return out

def need_update(board_version:str) -> bool:
    conf_dict = load_config()
    firmware_version = conf_dict['version'] 
    firmware_version = firmware_version.split(".")
    board_version = board_version.split(".")
    if (firmware_version is None) or (board_version is None):
        debug("NONETYPE HERE")
    booolean = __greater(firmware_version, board_version)
    if booolean: debug("Update needed!")
    return booolean


def __greater(outgoing:List[str], incoming:List[str]) -> bool:
    diff:int = len(incoming) - len(outgoing)
    if diff > 0: outgoing = pad_array(diff, outgoing)
    elif diff < 0: incoming = pad_array(0-diff, incoming)

    for i in range(len(outgoing)):
        if outgoing[i] > incoming[i]: return True

    return False

def timestamp_to_path(timestamp:str) -> str:
    timestamp = timestamp.replace(" ", "-")
    timestamp = timestamp.replace(":", "-")
    return timestamp