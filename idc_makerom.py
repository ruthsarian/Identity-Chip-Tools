import sys
import os
import glob
import wave
import audioop
import struct

ouput_pcm_sample_rate = 12000

# check that arguments were passed
if len(sys.argv) < 3:
	print("Usage: " + os.path.basename(sys.argv[0]) + " <files*.wav> <rom.bin> [RRGGBB]")
	sys.exit(1)

# do we have files?
files = glob.glob("./" + sys.argv[1])
if (len(files) < 1):
	print("No WAV files found. Exiting.")
	sys.exit(1)

#if os.path.exists(sys.argv[2]):
#	print("Specified ROM file already exists. Exiting.")
#	sys.exit(1)

# read in the WAV files
pcm_data = []
for wav_filename in files:

	# Open the input WAV file
	with wave.open(wav_filename, 'rb') as wav_in:

		# Get the input audio properties
		num_channels = wav_in.getnchannels()
		sample_width = wav_in.getsampwidth()
		original_sample_rate = wav_in.getframerate()

		# Calculate the conversion ratio
		ratio = original_sample_rate / ouput_pcm_sample_rate

		# Calculate the new number of frames
		num_frames = int(wav_in.getnframes() / ratio)

		# Prepare object to hold converted PCM data
		pcm_out = bytearray()

		# Read and convert audio data in chunks
		chunk_size = int(original_sample_rate / ratio)
		for _ in range(num_frames):

			# Read a chunk of audio data
			audio_data = wav_in.readframes(chunk_size)

			# Convert stereo to mono
			if num_channels == 2:
				audio_data = audioop.tomono(audio_data, sample_width, 1, 1)

			# Resample the audio data
			audio_data = audioop.ratecv(audio_data, sample_width, 1, original_sample_rate, ouput_pcm_sample_rate, None)[0]

			# Convert to 16-bit sample
			audio_data = audioop.lin2lin(audio_data, sample_width, 2)

			# swap endian-ness
			audio_data = audioop.byteswap(audio_data, 2)

			# lower 4 bits of each 16-bit sample need to be zeroed out
			# otherwise there are playback issues; maybe some sort of flag/special data is stored here?
			audio_data = bytearray(audio_data)
			for i in range(1, len(audio_data), 2):
				audio_data[i] &= 0xF0

			# Store the converted audio data
			pcm_out += audio_data

		if len(pcm_out) > 0:
			pcm_data.append(pcm_out)

#if len(files) != len(pcm_data):
#	print("Filename and PCM generated tracks differ!")
#	sys.exit(1)

with open(sys.argv[2], 'wb') as rom:

	# HEADER 1

	# number of tracks
##
## tested up to 14 tracks... may support more but untested
##

	rom.write(struct.pack(">h", len(pcm_data)))

	# address of start of address table (hard-coded)
	#rom.write(struct.pack(">i", 0x00000e)[1:])
	rom.write(bytes([0,0,0xe]))

	# ??
	#rom.write(struct.pack(">i", 0x000000)[1:])
	rom.write(bytes([0,0,0]))

	# address of end of address table
	rom.write(struct.pack(">i", 0x0e + (len(pcm_data) * 5))[1:])

	# ??
	#rom.write(struct.pack(">i", 0x000000)[1:])
	rom.write(bytes([0,0,0]))

	# start of address for audio track
	addr = 0x004000

	# write address table for tracks
	for pcm in pcm_data:

		# ?? audio type/marker
		rom.write(struct.pack(">h", 0x01ff))

		# address of start of pcm data
		rom.write(struct.pack(">i", addr)[1:])

		# advance addr; +10 is for the 10 0xFF bytes that end every track
		addr = addr + len(pcm) + 10

	# ? address to where ID & color is stored
	rom.write(bytes([0,0x10,0]))

	# ??
	rom.write(bytes([0,0x20,0]))

	# pad 0xFF until addres 0x0FF0
	for _ in range(0xFF0 - rom.tell()):
		rom.write(bytes([0xFF]))

	# ? unknown configuration data
#	rom.write(bytes([0x7A,0x8C,0x00,0x00,0x00,0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0A]))
# lets use the config data from the identity program chip
	rom.write(bytes([0xFE,0xCD,0x00,0x00,0x00,0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0A]))

###
###
### bytes 1000 & 1001 are ID... major and minor
### 0101 clu
### 0102 rinzer
### 0103 sam
### 0104 quora
### 0201 tron ID program
### 0301 doesn't work (didn't try higher)
### 
### rinzler ID is special - wave files 2+ flash blue regardless of disc color
###
###
	rom.write(bytes([0x02, 0x01]))

	# write RGB values of color for the identity chip

	# default color
	red = bytes([0xFF])
	grn = bytes([0xFF])
	blu = bytes([0xFF])

	# interpret color from command line arguments (if supplied)
	if len(sys.argv) > 3:
		
		try:
			colors = bytes.fromhex(sys.argv[3])
			print("Colors: " + sys.argv[3] + " (" + str(len(colors)) + ")")

			if len(colors) > 0:
				red = bytes([colors[0]])[-1:]
			if len(colors) > 1:
				grn = bytes([colors[1]])[-1:]
			if len(colors) > 2:
				blu = bytes([colors[2]])[-1:]
		except ValueError:
			print("ValueError")
			#pass

	rom.write(red)
	rom.write(grn)
	rom.write(blu)

	# pad 0xFF until addres 0x4000
	for _ in range(0x4000 - rom.tell()):
		rom.write(bytes([0xFF]))

	# write PCM data
	for pcm in pcm_data:
		rom.write(pcm)
		rom.write(bytes([0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]))

	# pad to 2mb in size
	for _ in range(0x200000 - rom.tell()):
		rom.write(bytes([0xFF]))

	print("ROM'd " + str(rom.tell())+ " bytes!")


###
###
### chip contains NO face data for identity disc program
###    face data is stored in the figure itself
###
### identity program audio files spaced evenly apart at 256KB
### --- is 256KB the max audio file size?  untested
###
