import json
import subprocess
import os
import re
import shutil

blackhole_header = "BlackHole/BlackHole/BlackHole.h"
header_backup = "temp/__BlackHole.h"

try:
    sudouid = os.environ['SUDO_UID']
except KeyError:
    print("This script should be run as sudo")
    exit()



def safeName(s):
   s = re.sub('[^0-9a-zA-Z_]', '', s)
   s = re.sub('^[^a-zA-Z_]+', '', s)
   return s

def makePatch(device):
    with open("template.patch.in") as template:
        template_str = template.read()
        patch = template_str.format(**device)
        patchfile_path = "temp/{}.patch".format(device["safe_name"])
        with open(patchfile_path, 'w') as patchfile:
            print("Create patch file {}".format(patchfile_path))
            patchfile.write(patch)
        return patchfile_path

def revertFile():
    shutil.copy(header_backup, blackhole_header)

def patchHeader(patchfile):
    subprocess.run(["patch", blackhole_header, patchfile]) 

def invokeXcodeBuild():
    print("Invoke xcodebuild")
    returned = subprocess.run(["xcodebuild", "build", 
                    "-project", "BlackHole/BlackHole.xcodeproj", 
                    "-configuration", "Release",
                    "-quiet",
                    "CONFIGURATION_BUILD_DIR=build",
                    "CODE_SIGNING_ALLOWED=NO"])
    print("xcodebuild returned {}".format(returned.returncode))

def extractBuiltDriver(device):
    driver_src = "BlackHole/build/BlackHole.driver"
    driver_dest = "output/BlackHole{}.driver".format(device["safe_name"])
    driver_installed = "/Library/Audio/Plug-Ins/HAL/BlackHole{}.driver".format(device["safe_name"])

    print("copy {} to {}".format(driver_src, driver_dest))
    if(os.path.exists(driver_dest)):
        shutil.rmtree(driver_dest)
    shutil.copytree(driver_src, driver_dest)

    print("install {} to {}".format(driver_src, driver_installed))
    try:
        if(os.path.exists(driver_installed)):
            shutil.rmtree(driver_installed)
        shutil.copytree(driver_src, driver_installed)
    except PermissionError as err:
        print("Could not install: {}".format(err))


def buildDevice(device):
    print("Build device driver for {}".format(device["name"]))
    device["safe_name"] = safeName(device["name"])
    patchfile = makePatch(device)
    patchHeader(patchfile)
    invokeXcodeBuild()
    revertFile()
    extractBuiltDriver(device)
    print("--- Finished building driver for '{}'".format(device["name"]))
    print()

with open("devices.json") as devicesfile:
    print("Checkout BlackHole.h from index")
    returned = subprocess.run(["git", "-C", "BlackHole", "checkout", "master", "--", "BlackHole/BlackHole.h"])
    print("git returned: {}".format(returned.returncode))
    print()

    devs = json.loads(devicesfile.read())
    if not os.path.exists("temp"):
        os.mkdir("temp")

    shutil.copy(blackhole_header, header_backup)

    for dev in devs:
        buildDevice(dev)

    print("Remove temp files")
    shutil.rmtree("temp")
    print("Restart CoreAudio")
    subprocess.run(["sudo", "launchctl", "kickstart", "-kp", "system/com.apple.audio.coreaudiod"])
    print("done")
