class PyAudioMock:  # pragma: no cover
    """Mocks the pyaudio package (only available with audio devices)."""
    class _StreamMock:
        def __init__(self, wav_file):
            self.wav_file = wav_file
            self.fhandle = open(self.wav_file, 'rb')

        def read(self, chunk_size, exception_on_overflow):  # pylint: disable=unused-argument
            """Read from the stream."""
            res = self.fhandle.read()
            self.fhandle.seek(0)
            return res

        def close(self):
            """Close the stream."""
            self.fhandle.close()

    def __init__(self, mock_wav):
        self.mock_wav = str(mock_wav)

    def __call__(self):
        return self

    def open(self, **kwargs):  # pylint: disable=unused-argument
        """Open a audio stream."""
        return self._StreamMock(self.mock_wav)

    def terminate(self):
        """Terminate the audio stream."""
