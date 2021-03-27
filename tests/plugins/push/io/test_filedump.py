import os
import tempfile

import pytest

from pnp.plugins.push.io import FileDump


@pytest.mark.asyncio
async def test_push():
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = FileDump(name='pytest', directory=tmpdir, binary_mode=False)
        created_file = await dut.push("I am the content")

        with open(created_file, 'r') as fs:
            assert fs.read() == "I am the content"


@pytest.mark.asyncio
async def test_push_envelope_filename_extension():
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = FileDump(name='pytest', directory=tmpdir, binary_mode=False)
        created_file = await dut.push({
            "payload": "I am the content",
            "file_name": "the_dump",
            "extension": "dmp"
        })

        assert created_file == os.path.join(tmpdir, "the_dump.dmp")
        with open(created_file, 'r') as fs:
            assert fs.read() == "I am the content"


def test_backwards_compat():
    from pnp.plugins.push.fs import FileDump
    _ = FileDump


def test_repr():
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = FileDump(name='pytest', directory=tmpdir, binary_mode=False)
        assert repr(dut) == (
            f"FileDump(binary_mode=False, directory='{tmpdir}', "
            f"extension='.dump', file_name=None, name='pytest')"
        )
