"""Module for interacting with multimodal large language models (LLMs).

This module provides abstractions for working with LLMs that can process
multimodal inputs (text, images, videos, etc.).
"""

import functools
import hashlib
import os
import time
from typing import Protocol
import file_io
import google
from google import genai
from google.genai import types as genai_types


PromptPart = str | file_io.File


class MultiModalLLMAdapater(Protocol):
  """Defines the interface for a multimodal LLM adapter.

  Adapters are responsible for interacting with specific LLM implementations,
  handling prompt construction, API calls, and response parsing.
  """

  def generate(
      self, prompt_parts: list[PromptPart], response_schema, temperature: float
  ) -> str:
    """Generates content based on the provided prompt parts.

    Args:
      prompt_parts: A list of prompt parts, which can be strings or files.
      response_schema: The expected schema of the LLM's response.
      temperature: The temperature setting for the LLM generation.

    Returns:
      The generated content as a string.
    """


class GeminiLLMAdapter(MultiModalLLMAdapater):
  """Adapter for interacting with the Gemini LLM.

  This adapter implements the `MultiModalLLMAdapater` protocol, providing
  a way to interact with the Gemini LLM using a consistent interface.
  It handles prompt construction, including incorporating files (images, videos)
  and managing the interaction with the Gemini API.
  """

  def __init__(
      self,
      client: genai.Client,
      model: str = "gemini-2.0-flash",
      system_prompt: str | None = None,
  ):
    self._client = client
    self._model = model
    self._system_prompt = system_prompt

  def _create_gemini_file_name(self, file_path: os.PathLike[str]) -> str:
    signature = hashlib.sha256()
    with open(file_path, "rb") as f:
      signature.update(f.read())
    return signature.hexdigest()[:40]

  def _get_file(self, name: str) -> genai_types.File | None:
    try:
      return self._client.files.get(name=name)
    # Exception for no access and file not found.
    except (
        genai.errors.ClientError,
        google.api_core.exceptions.PermissionDenied,
        google.api_core.exceptions.Forbidden,
    ):
      return None

  def _parse_prompt_part(self, prompt_part: PromptPart) -> genai_types.Content:
    """Parses a single prompt part into a Gemini-compatible content object.

    Supports strings and file.File objects.

    Args:
      prompt_part: The prompt part to parse (either a string or a file_io.File).

    Returns:
      A Gemini content object (string or genai_types.File).
    """
    if isinstance(prompt_part, str):
      return prompt_part
    elif isinstance(prompt_part, file_io.File):
      gemini_filename = self._create_gemini_file_name(prompt_part.name)
      file = self._get_file(gemini_filename)
      if not file:
        file = self._client.files.upload(
            file=prompt_part.name, config={"name": gemini_filename}
        )
        cleanup_callback = functools.partial(
            self._client.files.delete, name=gemini_filename
        )
        prompt_part.add_cleanup_callback(cleanup_callback)
        while True:
          if file.state == genai.types.FileState.PROCESSING:
            time.sleep(10)
            file = self._client.files.get(name=gemini_filename)
          else:
            break
      return file
    else:
      raise ValueError("Unsupported prompt part: ", prompt_part)

  def generate(
      self,
      prompt_parts: list[PromptPart],
      response_schema,
      temperature: float,
  ) -> str:
    """Generates content using the Gemini LLM.

    Args:
      prompt_parts: A list of prompt parts, which can be strings or file_io.File
        objects.
      response_schema: The expected schema of the LLM's response.
      temperature: The temperature setting for the LLM generation.

    Returns:
      The generated content as a string.
    """
    contents = [self._parse_prompt_part(part) for part in prompt_parts]
    response = self._client.models.generate_content(
        model=self._model,
        contents=contents,
        config=genai.types.GenerateContentConfig(
            response_mime_type=None
            if response_schema == str
            else "application/json",
            response_schema=None if response_schema == str else response_schema,
            temperature=temperature,
        ),
    )
    return response.text


class MultiModalLLM:
  """Represents a multimodal large language model.

  This class provides a high-level interface for interacting with an LLM
  through an adapter. It delegates the actual generation process to the
  provided adapter.
  """

  def __init__(self, adapter: MultiModalLLMAdapater):
    self.adapter = adapter

  def generate(
      self,
      prompt_parts: list[PromptPart],
      response_schema,
      temperature: float = 1.0,
  ) -> str:
    """Generates content using the configured LLM adapter.

    Args:
      prompt_parts: A list of prompt parts (text or files) to send to the LLM.
      response_schema: The expected schema of the LLM's response.
      temperature: The temperature setting for the LLM generation.

    Returns:
      The generated content as a string.
    """
    return self.adapter.generate(prompt_parts, response_schema, temperature)


def create_gemini_llm(
    model: str = "gemini-2.0-flash",
    system_prompt: str | None = None,
    api_key: str | None = None,
) -> MultiModalLLM:
  """Creates and returns a MultiModalLLM instance configured for Gemini.

  Args:
    model: The name of the Gemini model to use (e.g., "gemini-2.0-flash").
    system_prompt: An optional system prompt to guide the model's behavior.
    api_key: The API key for accessing the Gemini API. If None, it will attempt
      to read from the "GEMINI_API_KEY" environment variable.

  Returns:
    A MultiModalLLM instance.
  """
  client = genai.Client(api_key=api_key or os.environ["GEMINI_API_KEY"])
  adapter = GeminiLLMAdapter(
      client=client,
      model=model,
      system_prompt=system_prompt,
  )
  return MultiModalLLM(adapter)
