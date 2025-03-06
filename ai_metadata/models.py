"""Module for interacting with multimodal large language models (LLMs).

This module provides abstractions for working with LLMs that can process
multimodal inputs (text, images, videos, etc.).
"""

import os
from typing import Protocol
import file_io
import google.generativeai as google_genai


PromptPart = str | file_io.File


class MultiModalLLMAdapater(Protocol):

  def generate(
      self, prompt_parts: list[PromptPart], response_schema, temperature: float
  ) -> str:
    pass


class GeminiLLMAdapter(MultiModalLLMAdapater):
  """Adapter for interacting with the Gemini LLM.

  This adapter implements the `MultiModalLLMAdapater` protocol, providing
  a way to interact with the Gemini LLM using a consistent interface.
  It handles prompt construction, including incorporating files (images, videos)
  and managing the interaction with the Gemini API.
  """

  def __init__(
      self,
      model: google_genai.GenerativeModel,
      file_handler: file_io.GeminiFileHandler = file_io.GeminiFileHandler(),
  ):
    self._model = model
    self.file_handler = file_handler

  def _parse_prompt_part(
      self, prompt_part: PromptPart
  ) -> google_genai.types.ContentType:
    if isinstance(prompt_part, str):
      return prompt_part

    return self.file_handler.prepare(prompt_part)

  def generate(
      self,
      prompt_parts: list[PromptPart],
      response_schema,
      temperature: float,
  ) -> str:
    content_types = [self._parse_prompt_part(part) for part in prompt_parts]
    response = self._model.generate_content(
        content_types,
        generation_config=google_genai.GenerationConfig(
            response_mime_type="application/json"
            if response_schema != str
            else None,
            response_schema=response_schema if response_schema != str else None,
            temperature=temperature,
        ),
    )
    return response.text


class MultiModalLLM:

  def __init__(self, adapter: MultiModalLLMAdapater):
    self.adapter = adapter

  def generate(
      self,
      prompt_parts: list[PromptPart],
      response_schema,
      temperature: float = 1.0,
  ) -> str:
    return self.adapter.generate(prompt_parts, response_schema, temperature)


def create_gemini_llm(
    system_prompt: str = None,
    file_handler: file_io.GeminiFileHandler = file_io.GeminiFileHandler(),
    api_key: str | None = None,
) -> MultiModalLLM:
  google_genai.configure(api_key=api_key or os.environ["GEMINI_API_KEY"])
  gemini = google_genai.GenerativeModel(
      model_name="gemini-2.0-flash", system_instruction=system_prompt
  )
  adapter = GeminiLLMAdapter(gemini, file_handler)
  return MultiModalLLM(adapter)
