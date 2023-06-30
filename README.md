# Identity Chip Tools
This is a collection of python tools to manipulate ROMs of identity chips from the Tron Lightcycle / Run Identity Program.

## idc_dump.py
Given an identity chip image, it will extract all the audio into WAV files.

## idc_makerom.py
Given some WAV files, a path to output the ROM image to, and an RGB value, this script will generate a 4MB binary file that can then be written to an SPI flash chip such as the ones used in identity chips.
