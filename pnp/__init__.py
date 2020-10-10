"""Pull 'n' Push."""
import warnings

__version__ = "0.25.0"
__author__ = "Dennis Muth <d.muth@gmx.net>"


# https://stackoverflow.com/questions/40845304/  \
# runtimewarning-numpy-dtype-size-changed-may-indicate-binary-incompatibility
warnings.filterwarnings("ignore", message=".*numpy.dtype size changed.*")
warnings.filterwarnings("ignore", message=".*numpy.ufunc size changed.*")

warnings.filterwarnings("ignore", message=".*write permissions assigned to anonymous user.*")
