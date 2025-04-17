import sys
import wave
import os

# check that 
if len(sys.argv) != 2:
	print("Usage: " + os.path.basename(sys.argv[0]) + " <filename.bin>")
	sys.exit(1)

filename = sys.argv[1]

try:

	# open the ROM for editing
	with open(filename, 'rb') as rom:

		track_count = int.from_bytes(rom.read(2), byteorder='big', signed=False)
		print("There are %d tracks." % track_count)

		track_addr_tbl_addr = int.from_bytes(rom.read(3), byteorder='big', signed=False)
		print("Track address table located at 0x%06X." % track_addr_tbl_addr)

		for t in range(track_count):
			rom.seek(track_addr_tbl_addr + (t * 5) + 2)
			track_addr = (int.from_bytes(rom.read(3), byteorder='big', signed=False))
			print("Track %d is located at 0x%06X." % (t, track_addr))

			# record audio to wave file
			output_filename = os.path.splitext(filename)[0] + str(t) + '_audio.wav'
			wav_file = wave.open(output_filename, 'w')
			wav_file.setnchannels(1)
			wav_file.setsampwidth(2)
			wav_file.setframerate(12000)

			# go to start of audio data for the curren track
			rom.seek(track_addr);

			# read audio data and save to wave file
			while True:
				data = rom.read(2)
				if (data):

          # 10 bytes of 0xff mark the end of the wave data, but should not be included with the wave
          # if we find FF FF in the data, test if there are 8 more bytes of FF which signal the end of file,
          # otherwise keep processing the data like normal
					if (data == b'\xff\xff'):
						eof_check = rom.read(8)
						if (eof_check == b'\xff\xff\xff\xff\xff\xff\xff\xff'):
							break
						else:
							f.seek(-8, os.SEEK_CUR)

          # write the sample data to the output wav file
					sample = int.from_bytes(data, byteorder='big', signed=True)
					wav_file.writeframesraw(sample.to_bytes(2, byteorder='little', signed=True))
				else:
					break

			wav_file.close()

except FileNotFoundError:
	print(f"File {filename} not found.")
	sys.exit(1)

rom.close()
print("Done!")
