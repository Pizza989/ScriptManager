"""Manage Scripts running in the background"""

import os
import logging
import subprocess
import threading

import json


__all__ = ["start"]


with open("json/config.json", "r", encoding="utf-8") as file:
    config = json.load(file)
with open("json/settings.json", "r", encoding="utf-8") as file:
    settings = json.load(file)
    settings["path_to_id"] = dict(
        sorted(settings["path_to_id"].items(), key=lambda x: x[1])
    )  # Sort for later use

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s: %(name)s :%(levelname)s:- %(message)s"
)


def cleaner():
    logging.info("Cleaning...")
    for i, (path, _id) in enumerate(settings["path_to_id"].items()):
        if not os.path.exists(path):
            del settings["path_to_id"][path]
            for script in config["scripts"]:
                if script["path"] == path:
                    config["scripts"].remove(script)
            os.remove(f"logs/{_id}.log")
            if i + 1 == len(settings["path_to_id"]):
                return
            else:
                cleaner()


def handle_process(script: dict):
    # Create id for process if needed
    if not script["path"] in settings["path_to_id"]:
        settings["path_to_id"][script["path"]] = (
            int(list(settings["path_to_id"].values())[-1]) + 1
            if settings["path_to_id"]
            else 0  # A new unique id
        )

    # Setup process and logging
    process = subprocess.Popen(
        f"{script['executable']} {script['path']}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    os.mkdir(f"logs/{settings['path_to_id'][script['path']]}") if not os.path.isdir(
        f"logs/{settings['path_to_id'][script['path']]}"
    ) else ()

    sh = logging.StreamHandler()
    sh.setFormatter(
        logging.Formatter("%(asctime)s: %(name)s :%(levelname)s:- %(message)s")
    )

    out_logger = logging.getLogger(f"Output: {script['name']}")
    out_logger.addHandler(
        logging.FileHandler(f"logs/{settings['path_to_id'][script['path']]}/stdout.log")
    )
    out_logger.addHandler(sh)
    err_logger = logging.getLogger(f"Error: {script['name']}")
    err_logger.addHandler(
        logging.FileHandler(f"logs/{settings['path_to_id'][script['path']]}/stderr.log")
    )
    err_logger.addHandler(sh)
    while True:
        out, err = process.stdout.readline(), process.stderr.readline()
        out_logger.info(out.decode().strip("\r\n"))
        err_logger.error(err.decode().strip("\r\n"))
        if not process.poll():
            outs, errs = process.stdout.readlines(), process.stderr.readlines()
            for out, err in zip(outs, errs):
                out_logger.info(out.decode().strip("\r\n"))
                err_logger.error(err.decode().strip("\r\n"))
            exit()


def start():
    try:
        for script in config["scripts"]:
            if not os.path.exists(script["path"]):
                logging.warning(f"Path: {script['path']} does not exist.")
                cleaner()
                continue

            logging.info(
                f"{script['path']} has been started using {script['executable']}..."
            )
            threading.Thread(target=handle_process, args=(script,)).start()
    finally:
        with open("json/settings.json", "w", encoding="utf-8") as file:
            logging.info("Updating settings file...")
            json.dump(settings, file)
        with open("json/config.json", "w", encoding="utf-8") as file:
            logging.info("Updating config file...")
            json.dump(config, file)


if __name__ == "__main__":
    start()
