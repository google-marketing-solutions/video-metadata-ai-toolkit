"""Module for file management and interaction with LLMs."""

import os
from typing import Callable


class File:
  """Represents a file to be used with a multimodal LLM.

  This class encapsulates the name/path of a local file and provides a mechanism
  for registering cleanup callbacks.  These callbacks are executed
  when the `cleanup` method is called, typically after the file has
  been processed by the LLM.
  """

  def __init__(self, name: str | os.PathLike[str]):
    self.name = name
    self._cleanup_callbacks: list[Callable[[], None]] = []

  def add_cleanup_callback(self, callback: Callable[[], None]) -> None:
    """Adds a callback function to be executed during cleanup.

    The provided callback function will be called when the `cleanup` method
    is invoked on the `File` object. This allows for registering actions
    to be performed during file cleanup, such as deleting temporary files
    or releasing resources.

    Args:
      callback: A callable function that takes no arguments and returns None.
        This function will be executed during cleanup.
    """
    self._cleanup_callbacks.append(callback)

  def cleanup(self) -> None:
    """Executes all registered cleanup callbacks.

    Callbacks are added using the `add_cleanup_callback` method.
    """
    for cleanup_callback in self._cleanup_callbacks:
      cleanup_callback()
