"""Pull 'n' Push Sound recorder."""
import sys

import click

CHANNELS = 1
RATE = 44100
CHUNK = 512


def list_devices(ctx, param, value):
    """List all available microphone devices."""
    _ = param  # Fake usage
    if not value or ctx.resilient_parsing:
        return

    try:
        import pyaudio
    except ImportError:
        print("You have to install extra 'sound' in order to use this shell script")
        ctx.exit(99)
        return  # Never reached, but linters do not know about it

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
    ctx.exit()


@click.command('pnp_record_sound')
@click.argument(
    'output_file',
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    required=True
)
@click.option(
    '--seconds',
    type=click.INT,
    default=1, show_default=True,
    help="Number of seconds to record."
)
@click.option(
    '--index',
    type=click.INT,
    default=None,
    help="Optionally specify the index of the mic to record the sound."
)
@click.option(
    '--list',
    is_flag=True,
    callback=list_devices,
    expose_value=False,
    is_eager=True,
    help="Shows all available mic devices and their associated index and exit."
)
def main(output_file, seconds, index):
    """Pull 'n' Push Sound recorder."""
    try:
        import pyaudio
        import wave
    except ImportError:
        print("You have to install extra 'sound' in order to use this shell script")
        sys.exit(99)

    fmt = pyaudio.paInt16
    pa = pyaudio.PyAudio()
    if index is not None and index > pa.get_device_count() - 1:
        print("Device index is out of bounds")
        sys.exit(1)
    if index is not None:
        device = pa.get_device_info_by_index(index)
        if device.get('maxInputChannels', 0) == 0:
            print("Device @ index {index} is not an input device (microphone)".format(**locals()))
            sys.exit(2)
        if device.get('maxInputChannels', 0) < CHANNELS:
            print("Device @ index {index} does not support {channels} channels".format(
                index=index, channels=CHANNELS
            ))
            sys.exit(3)

    buffer = []
    input("Press any key to start the recording")
    stream = pa.open(
        format=fmt,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=index,
        frames_per_buffer=CHUNK
    )

    try:
        for _ in range(0, int(RATE / CHUNK * seconds)):
            data = stream.read(CHUNK)
            buffer.append(data)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    out_file = wave.open(output_file, 'wb')
    out_file.setnchannels(CHANNELS)
    out_file.setsampwidth(pa.get_sample_size(fmt))
    out_file.setframerate(RATE)
    out_file.writeframes(b''.join(buffer))
    out_file.close()

    print("Wave file written to {out_wav} @ {rate} Hz".format(out_wav=output_file, rate=RATE))


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
