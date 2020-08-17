# SupermassiveBlackHole

## What

This is just a build-script written in python that will automatically build multiple versions of the [BlackHole](https://github.com/ExistentialAudio/BlackHole) Loopback driver.

## Requirements

You will need a functioning Xcode build environment on your mac. Either Xcode or just the Xcode Command Line Tools

## Usage

Clone this repository with its submodules 

```bash
$ git clone https://github.com/jonasohland/SupermassiveBlackHole --recursive
```

Edit `devices.json` to add or remove devices and run `buildthem.py` from the root of this repository

```bash
$ sudo python buildthem.py
```

and you are done


Please consider sponsoring [ExistentialAudio](https://github.com/sponsors/ExistentialAudio), the makers of the BlackHole driver.