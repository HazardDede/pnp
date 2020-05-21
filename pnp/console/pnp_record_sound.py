"""Pull 'n' Sound recorder

Usage:
  pnp_record_sound <output_file> <seconds> [--index=<idx>]
  pnp_record_sound --list
  pnp_record_sound (-h | --help)

Options:
  -h --help         Show this screen.
  --list            Shows all available mic devices and their associated index

Args:
  output_file       File to write (wav)
  seconds           Number of seconds to record
  --index=<idx>     Optionally specify the index of the mic to record the sound

"""

CHANNELS = 1
RATE = 44100
CHUNK = 512


def run(out_wav, secs, idx):
    """
    Run the sound recorder.

    Args:
        out_wav (str): File path where to store the recorded sound.
        secs (int): Number of seconds to record.
        idx (Optional[int]): The device index to use or None (first qualified device).
    """
    try:
        import pyaudio
        import wave
    except ImportError:
        print("You have to install extra 'sound' in order to use this shell script")
        return 99

    fmt = pyaudio.paInt16
    pa = pyaudio.PyAudio()
    if idx is not None and idx > pa.get_device_count() - 1:
        print("Device index is out of bounds")
        return 1
    if idx is not None:
        device = pa.get_device_info_by_index(idx)
        if device.get('maxInputChannels', 0) == 0:
            print("Device @ index {idx} is not an input device (microphone)".format(**locals()))
            return 2
        if device.get('maxInputChannels', 0) < CHANNELS:
            print("Device @ index {idx} does not support {channels} channels".format(
                idx=idx, channels=CHANNELS
            ))
            return 3

    buffer = []
    input("Press any key to start the recording")
    stream = pa.open(
        format=fmt,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=idx,
        frames_per_buffer=CHUNK
    )

    try:
        for _ in range(0, int(RATE / CHUNK * secs)):
            data = stream.read(CHUNK)
            buffer.append(data)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    out_file = wave.open(out_wav, 'wb')
    out_file.setnchannels(CHANNELS)
    out_file.setsampwidth(pa.get_sample_size(fmt))
    out_file.setframerate(RATE)
    out_file.writeframes(b''.join(buffer))
    out_file.close()

    print("Wave file written to {out_wav} @ {rate} Hz".format(out_wav=out_wav, rate=RATE))
    return 0


def list_devices():
    """List all available microphone devices."""
    try:
        import pyaudio
    except ImportError:
        print("You have to install extra 'sound' in order to use this shell script")
        return 99

    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        dev = pa.get_device_info_by_index(i)
        input_chn = dev.get('maxInputChannels', 0)
        if input_chn > 0:
            name = dev.get('name')
            rate = dev.get('defaultSampleRate')
            print("Index {i}: {name} (Max Channels {input_chn}, Default @ {rate} Hz)".format(
                i=i, name=name, input_chn=input_chn, rate=int(rate)

            ))
    return 0


def main():
    """Main entry point to runner pnp_record_sound."""
    from docopt import docopt
    arguments = docopt(__doc__)
    if arguments.get('--list', False):
        return list_devices()

    out_wav, secs, idx = (
        arguments['<output_file>'],
        int(arguments['<seconds>']),
        arguments.get('--index', None)
    )
    return run(out_wav, secs, idx and int(idx))


if __name__ == '__main__':
    import sys
    sys.exit(main())
