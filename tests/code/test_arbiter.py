"""
datazen - Test the DataArbiter implementation.
"""

# built-in
from io import StringIO
from os import linesep
from pathlib import Path
from tempfile import NamedTemporaryFile

# module under test
from datazen.code import ARBITER


def test_arbiter_decode_stream_basic():
    """Test that we can decode data from a stream."""

    with StringIO('{"a": 1, "b": 2, "c": 3}') as stream:
        result = ARBITER.decode_stream("json", stream)
        assert result.success
        assert result.data == {"a": 1, "b": 2, "c": 3}


def test_arbiter_decode_basic():
    """Test that we correctly fail to decode data from a file."""

    with NamedTemporaryFile("w", suffix=".json") as tmp:
        # Write (malformed) data to the file.
        tmp.write('{"a": 1, "b": 2, "c": 3')
        tmp.write(linesep)
        tmp.flush()

        result = ARBITER.decode(Path(tmp.name))
        assert not result.success
