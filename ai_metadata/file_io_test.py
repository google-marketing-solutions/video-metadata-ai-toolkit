"""Unit tests for the file_io module."""

import unittest
from unittest import mock

import file_io


class FileTest(unittest.TestCase):

  def test_cleanup_calls_callbacks(self):
    file = file_io.File("name")
    mock_callback1 = mock.MagicMock()
    mock_callback2 = mock.MagicMock()
    file.add_cleanup_callback(mock_callback1)
    file.add_cleanup_callback(mock_callback2)

    file.cleanup()

    mock_callback1.assert_called_once()
    mock_callback2.assert_called_once()


if __name__ == "__main__":
  unittest.main()
