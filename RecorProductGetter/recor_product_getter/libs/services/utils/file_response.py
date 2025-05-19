from typing import Iterator

"""
ijson works with file-like objects; that is, objects with a read method
wrap the response to make it look like a file that can be read
"""


class FileResponse:
    """
    Wraps a response object to provide a file-like interface for ijson.
    """

    def __init__(self, data: Iterator[bytes]):
        """
        Initializes the FileResponse.

        Args:
            data: An iterator of bytes, typically from a response's iter_content.
        """
        self.data = data

    def read(self, n: int) -> bytes:
        """
        Reads up to n bytes from the data iterator.

        Args:
            n: The number of bytes to read.

        Returns:
            The bytes read.
        """
        if n == 0:
            return b""
        try:
            return next(self.data, b"")
        except StopIteration:
            return b""
