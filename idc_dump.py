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
			eof_count = 0

			# read audio data and save to wave file
			while True:
				data = rom.read(2)
				if (data):
					sample = int.from_bytes(data, byteorder='big', signed=True)
					wav_file.writeframesraw(sample.to_bytes(2, byteorder='little', signed=True))
					if (data == b'\xff\xff'):
						eof_count = eof_count + 1
						if (eof_count == 5):
							break
					else:
						eof_count = 0
				else:
					break

			wav_file.close()
###
### gross way to remove xff from end of audio files extracted
###
			wave_file = open(os.path.splitext(filename)[0] + str(t) + '_audio.wav',"a");
			wave_size = os.path.getsize(os.path.splitext(filename)[0] + str(t) + '_audio.wav')
			wave_file.truncate(wave_size-10)

except FileNotFoundError:
	print(f"File {filename} not found.")
	sys.exit(1)

rom.close()
print("Done!")
