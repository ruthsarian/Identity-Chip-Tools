# Identity Chip Tools
This is a collection of [python](https://www.python.org/) tools to manipulate ROMs of identity chips from the [Tron Lightcycle / Run](https://disneyworld.disney.go.com/attractions/magic-kingdom/tron-lightcycle-run/) [Identity Program](https://disneyworld.disney.go.com/shops/magic-kingdom/tron-identity-program/).

These tools have only been tested with a character identity chip. The Identity Program allows you to create your own identity chip that includes both audio AND images. The character chips do not appear to contain images so these tools do not take image data into account. If I am ever able to obtain an image of an identity program chip I will update these tools.

## idc_dump.py
Given an identity chip image, it will extract all the audio into WAV files.

## idc_makerom.py
Given some WAV files, a path to output the ROM image to, and an RGB value, this script will generate a 4MB binary file that can then be written to an SPI flash chip such as the ones used in identity chips.

# Identity Chip PCB
Here is [the front](https://flic.kr/p/2oHpdiG) and [back](https://flic.kr/p/2oHr6PE) of the PCB inside an identity chip. It uses a 2MB SPI flash memory chip (specifically an [XT25F16B](https://www.lcsc.com/search?q=XT25F16BDFIGT) from [XTX Tech](http://www.xtxtech.com/)) The PCB includes a pinout of the gold fingers that are exposed when the PCB is inside its plastic cover. 

I have designed [a PCB that uses an 150-mil SOIC8 flash memory chip](https://oshpark.com/shared_projects/ksdo1SBA) soldered into a hole in the center of the PCB in order to fit within the identity chip socket. *Use at your own risk.*

# ROM Details
Audio is stored as big endian 16-bit mono PCM data with a sample rate of 12KHz (same sample rate as Droid Depot personality chip audio). The lower 4 bits of each sample need to be zero. Starting at 0x00000E of the ROM is an address table. Each entry is 5 bytes, the first two bytes are 0x01FF and the following 3 bytes are the address for the audio data. At offset 0x001002 is a 3 byte value that represents the color the LEDs will display when the chip is inserted. The first byte represents the red value, the second byte is the green value, the third byte is the blue value.
