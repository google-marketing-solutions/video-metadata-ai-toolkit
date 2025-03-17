"""Module for file management and interaction with LLMs."""

import os
import time
from typing import Callable
import google
import google.api_core
import google.api_core.exceptions
import google.generativeai as google_genai


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


class GeminiFileHandler:
  """Handles file interactions with Gemini."""

  def _convert_to_gemini_file_name(self, file_name: str) -> str:
    return "".join(c for c in file_name if c.isalnum()).lower()

  def upload(self, file: File) -> google_genai.types.File:
    """Uploads the given file to Gemini.

    Args:
      file: The `File` object to upload.

    Returns:
      A `google_genai.types.File` object representing the uploaded file.
    """
    file_name = self._convert_to_gemini_file_name(file.name)
    return google_genai.upload_file(path=file.name, name=file_name)

  def get(self, file: File) -> google_genai.types.File | None:
    """Attempts to retrieve the file from Gemini.

    Args:
      file: The `File` object representing the file to retrieve.

    Returns:
      A `google_genai.types.File` object if the file is found, otherwise None.
    """
    try:
      file_name = self._convert_to_gemini_file_name(file.name)
      return google_genai.get_file(file_name)
    # Exception for no access and file not found.
    except (
        google.api_core.exceptions.PermissionDenied,
        google.api_core.exceptions.Forbidden,
    ):
      return None

  def wait_for_processing(
      self, file: google_genai.types.File
  ) -> google_genai.types.File:
    """Waits for a Gemini file to finish processing.

    This method polls the status of the given file until it is no longer in the
    "PROCESSING" state.  It retrieves the current state at 10-second intervals.

    Args:
      file: The `google_genai.types.File` object to wait for.

    Returns:
      The `google_genai.types.File` object, updated with its final state.
    """
    gemini_file = file
    while True:
      if gemini_file.state.name == "PROCESSING":
        time.sleep(10)
        gemini_file = google_genai.get_file(gemini_file.name)
      else:
        break
    return gemini_file

  def prepare(self, file: File) -> google_genai.types.File:
    """Prepares a file for use with Gemini.

    This method uploads the file (or retrieves it if it already exists) to the
    Gemini file storage. The method returns when the file is ready to be used
    with Gemini.

    Args:
      file: The `File` object to prepare.

    Returns:
      A `google_genai.types.File` object ready for use with Gemini.
    """
    gemini_file = self.get(file)
    if not gemini_file:
      gemini_file = self.upload(file)
      file.add_cleanup_callback(gemini_file.delete)
    return self.wait_for_processing(gemini_file)
