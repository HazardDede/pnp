"""Sound related shared stuff."""

import logging
import os

import attr

from ..validator import Validator


_LOGGER = logging.getLogger(__file__)


MODE_PEARSON = 'pearson'
MODE_STD = 'std'
ALLOWED_MODES = [MODE_PEARSON, MODE_STD]


def perform_fft(signal, rate, add_zeros=True):
    """Perform a fast fournier transformation on a given signal."""
    import numpy as np
    import scipy

    chn = len(signal.shape)
    if chn >= 2:  # Make mono channel
        signal = signal.sum(axis=1) / 2
    N = int(signal.shape[0])
    secs = N / float(rate)
    if add_zeros:
        signal = np.concatenate((signal, np.zeros(len(signal))), axis=None)
    trans_fft = abs(scipy.fft(signal))

    return N, secs, trans_fft


def similarity_pearson(buffer, wav_file, rate, threshold):
    """Check the similarity of a recorded sound buffer and a given wav_file.
    Use the pearson correlation."""
    _, _, current_fft = perform_fft(buffer[:wav_file.signal_length], rate, True)
    from scipy.stats.stats import pearsonr
    corrcoef = pearsonr(wav_file.signal_fft, current_fft)[0]

    return corrcoef >= threshold, corrcoef, threshold


def similarity_std(buffer, wav_file, rate, threshold):
    """Check the similarity of a recorded sound buffer and a given wav_file.
    Use a correlation check using the standard deviation."""
    import numpy as np
    _, _, current_fft = perform_fft(buffer[:wav_file.signal_length], rate, True)
    corrcoef = np.correlate(
        wav_file.signal_fft / wav_file.signal_fft.std(),
        current_fft / current_fft.std()
    )[0] / len(wav_file.signal_fft)

    return corrcoef >= threshold, corrcoef, threshold


@attr.s
class WavFile:
    """Wav file representation including. FFT representation."""
    abs_path = attr.ib()
    _file_name = attr.ib(default=None, repr=False)
    _signal_fft = attr.ib(default=None, repr=False)
    _signal_length = attr.ib(default=None, repr=False)

    @property
    def file_name(self):
        """Return the name of the wav file (without path)."""
        return os.path.basename(os.path.splitext(self.abs_path)[0])

    @property
    def signal_fft(self):
        """Return the fft representation of this wav file."""
        if self._signal_fft is None:
            self._signal_length, self._signal_fft = self._load_wav_fft()
        return self._signal_fft

    @property
    def signal_length(self):
        """Return the signal length of this wav file."""
        if not self._signal_length:
            self._signal_length, self._signal_fft = self._load_wav_fft()
        return self._signal_length

    def _load_wav_fft(self):
        import scipy.io.wavfile as wavfile
        _LOGGER.debug("Loading wav file from '%s'", self.abs_path)
        sample_rate, signal = wavfile.read(self.abs_path)
        N, secs, signal_fft = perform_fft(signal, sample_rate)
        _LOGGER.debug("Loaded %s seconds wav file @ %s hz", secs, sample_rate)
        return N, signal_fft

    @classmethod
    def from_path(cls, wav_file, base_path):
        """Load the wav file from a relative or absolute path."""
        def _mk_abs(file_item):
            file_item = str(file_item)
            if os.path.isabs(file_item):
                return file_item
            return os.path.join(base_path, file_item)

        wav_file = str(wav_file)
        abs_path = _mk_abs(wav_file)
        Validator.is_file(wav_file=abs_path)

        return WavFile(abs_path)
