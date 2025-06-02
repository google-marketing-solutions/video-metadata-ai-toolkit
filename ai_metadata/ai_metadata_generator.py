# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module to process video files and generate AI attributes.

When run from the CLI, this module can be used to processes a video with
artificial intelligence to generate metadata related to the content.

usage: ai_metadata_generator.py [-h] [--keys KEYS [KEYS ...]] [--vertex]
{describe,summarize,tag,title,iab} content_file

Analyzes content using AI.

positional arguments:
  {describe,summarize,tag,title,iab}
                        The action to perform for the provided content. Valid
                        actions are:
                          title: suggests possible titles for the content
                          describe: describes the content with as much detail as
                          possible
                          summarize: summarizes the content for an external
                          audience
                          tag: identifies keywords related to the content (use
                          with --keys to specify custom keys)
                          iab: identifies IAB content and audience categories
                          related to the content
  content_file          The URI of the content to be processed (local files
  only).

options:
  -h, --help            show this help message and exit
  --keys KEYS [KEYS ...]
                        Use with "tag" to create key/values instead of free-form
                        metadata values. No-op otherwise.
  --vertex, -v          Use Vertex AI. Requires Application Default Credentials
  with a default project to be configured.
"""

import argparse
import copy
import dataclasses
import json
import sys
import textwrap
from typing import Sequence
import file_io
import iab
import models
import project_configs
import transcription_utils
import video_class

Content = str | file_io.File


def _generate_from_content(
    content: Content | list[Content],
    instructions: str,
    user_instructions: str,
    language_model: models.MultiModalLLM,
    response_schema,
    temperature: float,
) -> str:
  """Generates text using an LLM for the provided content and instructions.

  Args:
    content: The content to be used as input for the language model. For list
      inputs, the entire list is treated as one piece of content.
    instructions: Specific instructions for the language model on how to process
      the content.
    user_instructions: Additional instructions from the user.
    language_model: The language model to use for generation.
    response_schema: The expected schema of the response.
    temperature: The temperature parameter for the language model.

  Returns:
    The generated text as a string.
  """
  content_parts = content if isinstance(content, list) else [content]
  prompt = [*content_parts, instructions]
  prompt += (
      [f"**Additional Instructions:** {user_instructions}"]
      if user_instructions
      else []
  )
  return language_model.generate(prompt, response_schema, temperature)


def suggest_titles(
    content: Content | list[Content],
    additional_instructions: str = "",
    language_model: models.MultiModalLLM | None = None,
) -> list[str]:
  """Suggests titles for the provided content using an LLM.

  Args:
    content: The content (text, video, etc.) for which to generate titles. Can
      be a single ContentType or a list. For list inputs, the entire list is
      treated as one piece of content.
    additional_instructions: Any additional instructions for title generation.
    language_model: The language model to use for generating titles. Defaults to
      a Gemini LLM.

  Returns:
    A list of suggested titles.
  """
  language_model = language_model or models.create_gemini_llm()
  prompt = textwrap.dedent("""\
    You are a creative and experienced headline/title generator for a leading
    media company. You specialize in crafting compelling and engaging titles for
    a variety of content, including video content and text articles. Your goal
    is to help content editors create titles that attract readers/viewers,
    accurately reflect the content, and drive engagement.

    Key Responsibilities:
    - Understand the nuances of different content types: You can differentiate
    between titles for videos and articles and tailor your suggestions
    accordingly.
    - Generate multiple title options: You will offer a diverse range of title
    suggestions based on the provided context.
    - Adapt to different tones and styles: You can adjust the tone of the title
    to match the content, whether it's serious, humorous, informative, or
    sensational.
    - The title should clearly convey the main topic or theme of the content.
    - The title should pique the reader's/viewer's curiosity and encourage them
    to click.
    - The title should accurately reflect the content and avoid misleading or
    clickbait tactics.
    - Keep titles concise and to the point where possible, but prioritize
    clarity and impact over arbitrary length limits.
  """)
  response_text = _generate_from_content(
      content,
      prompt,
      additional_instructions,
      language_model,
      list[str],
      1.2,
  )
  return json.loads(response_text)


def describe(
    content: Content | list[Content],
    additional_instructions: str = "",
    language_model: models.MultiModalLLM | None = None,
) -> str:
  """Generates a detailed description of the provided content using an LLM.

  Args:
      content: The content to describe (text, video, images). For list inputs,
        the entire list is treated as one piece of content.
      additional_instructions: Additional instructions to guide the description
        generation.
      language_model: The language model to use. Defaults to a Gemini LLM.

  Returns:
      A detailed description of the content.
  """
  language_model = language_model or models.create_gemini_llm()
  prompt = textwrap.dedent("""\
    You are a Content Analyst for a major media company. Your role is to
    thoroughly analyze and describe various media content, including videos,
    images, and articles. Your descriptions should be detailed, accurate, and
    written in complete, grammatically correct sentences.

    Key Responsibilities:
    - Describe the content in detail:  Provide a comprehensive description of
    what is shown or written in the content. Include relevant details such as:
      * For videos: Setting, characters, actions, dialogue (if clear and
      relevant), overall narrative or message, and any notable visual or
      auditory elements.
      * For images: Subject, composition, colors, lighting, style, and any
      discernible context or message.
      * For articles: Topic, main points, arguments, tone, writing style, and
      intended audience.
    - Be objective: Focus on describing what is present in the content without
    adding personal opinions or interpretations.
    - Be thorough:  Aim for a detailed description that captures the essence
    of the content.
    - Use precise language: Choose words carefully to accurately convey the
    details of the content.

    Your analysis is crucial for content cataloging, searchability, and
    understanding the company's media assets.
  """)
  return _generate_from_content(
      content,
      prompt,
      additional_instructions,
      language_model,
      str,
      1.2,
  )


def summarize(
    content: Content | list[Content],
    additional_instructions: str = "",
    language_model: models.MultiModalLLM | None = None,
) -> str:
  """Summarizes the given content using a language model.

  Args:
      content: The content to summarize. For list inputs, the entire list is
        treated as one piece of content.
      additional_instructions: Any additional instructions for summarization.
      language_model: The language model to use. Defaults to a Gemini LLM.

  Returns:
      A summary of the content.
  """
  language_model = language_model or models.create_gemini_llm()
  prompt = textwrap.dedent("""\
    You are a highly skilled content summarization agent working for a media
    company. Your primary function is to create engaging and informative
    summaries for various types of media content, including movies, TV shows,
    documentaries, and short-form videos. These summaries will be used in a
    content library and potentially displayed on a streaming service platform.
    Your summaries should cater to a general audience and entice viewers to
    watch the full content.

    Key Responsibilities:
    - Generate concise and captivating summaries: Focus on the core plot, key
    characters, and unique selling points of the content. Avoid spoilers and
    maintain a neutral tone, unless otherwise specified.
    - Understand target audience: Write for a general audience unless specific
    demographic information is provided. Assume the audience is interested in
    discovering new content but may not be familiar with the specific title.
    - Maintain a consistent style and tone: Use clear, concise language, and
    avoid jargon or overly technical terms. Strive for a professional yet
    engaging tone that sparks interest.
    - Prioritize accuracy and avoid speculation: Base your summaries solely on
    the provided information (e.g., transcripts, plot outlines, existing
    descriptions). Do not invent plot details or speculate about character
    motivations.

    Output format: Format your summaries as plain text.
  """)
  return _generate_from_content(
      content,
      prompt,
      additional_instructions,
      language_model,
      str,
      1.2,
  )


@dataclasses.dataclass
class KeyValue:
  key: str
  allowed_values: list[str] | iab.Taxonomy


_PROMPT_KEY_VALUES = """\
You are a highly skilled Ad Targeting Specialist responsible for maximizing the\
advertising revenue potential of multimedia content. Your task is to \
accurately assign values to a set of keys, selecting from provided lists when
available, and generating relevant values when lists are not provided. Your \
primary goal is to choose values that are highly relevant to potential \
advertisers.

**Keys and Allowed Values (if applicable):**
{allowed_values}

**Instructions:**

1. **Carefully review the input content.** Understand its core topics, themes, \
and key elements *in the context of potential advertising*.
2. **For *each* key, follow these rules:**
  - **If Allowed Values are provided:** Select the most relevant values *from \
an advertising perspective* from the corresponding list. Prioritize values \
that are likely to be used as keywords by advertisers targeting this type of \
content. Do *not* generate any values outside of the provided list.
  - **If Allowed Values are *not* provided (the key is listed, but the only \
value is "Any"):** Generate values that are highly relevant to advertisers. \
Consider:
    - **Common Advertising Categories:** Think about categories like "Travel," \
"Technology," "Food & Beverage," "Finance," "Automotive," "Fashion," etc., and \
how the video content might relate.
    - **Target Audience Interests:**  Align your generated values with the \
interests and demographics of the most likely target audience.
    - **Keywords:** Use terms that advertisers would likely use to target this \
content.
3. **Strict Adherence (for keys with Allowed Values):** When allowed values \
*are* provided, it is *critical* that you *only* use the exact values from \
the list. Do not modify, rephrase, or add any words. Copy the allowed values \
*exactly* as they appear.  Prioritize advertising relevance when selecting.
"""


def generate_key_values(
    content: Content | list[Content],
    keys: list[str | KeyValue],
    additional_instructions: str = "",
    language_model: models.MultiModalLLM | None = None,
) -> dict[str, list[str] | list[iab.TaxonomyEntity]]:
  """Generates key-value pairs based on the provided content.

  Args:
      content: The content to analyze. For list inputs, the entire list is
        treated as one piece of content.
      keys: A list of keys or KeyValue objects for which to generate values.
      additional_instructions: Additional instructions for generation.
      language_model: The language model to use. Defaults to a Gemini LLM.

  Returns:
      A dictionary where the keys are the provided keys and values are lists of
      generated strings, or, TaxonomyEntities if the keys were restricted to a
      specific Taxonomy.
  """
  language_model = language_model or models.create_gemini_llm()

  metadata_keys = [
      key if isinstance(key, KeyValue) else KeyValue(key, []) for key in keys
  ]
  # Creates a string representation of each key and its allowed values (or "Any"
  # for an unbounded key) to be added to the prompt:
  #
  # Key: <key_name>
  #   <allowed value 1>
  #   <allowed value 2>
  #   ...
  #
  # Key: <key_name>
  #   Any
  lines = []
  for key_value in metadata_keys:
    lines.append("")
    lines.append(f"Key: {key_value.key}")
    if isinstance(key_value.allowed_values, iab.Taxonomy):
      value_list = key_value.allowed_values.tolist()
    else:
      value_list = key_value.allowed_values

    if value_list:
      lines.extend([f"  {val}" for val in value_list])
    else:
      lines.append("  Any")

  allowed_values = "\n".join(lines)

  response_schema = {
      "type": "object",
      "properties": {
          key_value.key: {
              "type": "array",
              "items": {
                  "type": "string",
              },
          }
          for key_value in metadata_keys
      },
      "required": [key_value.key for key_value in metadata_keys],
  }
  response_text = _generate_from_content(
      content,
      _PROMPT_KEY_VALUES.format(allowed_values=allowed_values),
      additional_instructions,
      language_model,
      response_schema,
      0.0,
  )
  response_dict = json.loads(response_text)
  for metadata_key in metadata_keys:
    if metadata_key.key not in response_dict:
      values = []
    elif isinstance(metadata_key.allowed_values, iab.Taxonomy):
      taxonomy = metadata_key.allowed_values
      values = taxonomy.get_entities_by_name(response_dict[metadata_key.key])
    elif metadata_key.allowed_values:
      values = [
          value
          for value in response_dict[metadata_key.key]
          if value in metadata_key.allowed_values
      ]
      values = response_dict[metadata_key.key]
    else:
      continue
    response_dict[metadata_key.key] = values

  return response_dict


def generate_metadata(
    content: Content | list[Content],
    allowed_values: list[str] | None = None,
    additional_instructions: str = "",
    language_model: models.MultiModalLLM | None = None,
) -> list[str]:
  """Generates free-form metadata tags for the provied content using an LLM.

  Args:
      content: The content for which to generate metadata. For list inputs, the
        entire list is treated as one piece of content.
      allowed_values: An optional set of allowed values for the output metadata.
        If no values are provided, the metadata will be generated free-form.
      additional_instructions:  Additional instructions for metadata generation.
      language_model: The language model to use. Defaults to a Gemini LLM.

  Returns:
      A list of metadata strings.
  """
  metadata_key = KeyValue("keyword", allowed_values or [])
  key_values = generate_key_values(
      content, [metadata_key], additional_instructions, language_model
  )
  return key_values["keyword"]


def generate_iab_categories(
    content: Content | list[Content],
    additional_instructions: str = "",
    language_model: models.MultiModalLLM | None = None,
) -> list[iab.TaxonomyEntity]:
  """Generates IAB categories for the provided content.

  Analyzes the content and assigns relevant IAB (Interactive Advertising Bureau)
  categories. It fetches the latest IAB content and audience taxonomies, then
  uses the language model to determine the most appropriate categories for the
  given content.

  Args:
    content: The content for which to generate metadata. For list inputs, the
      entire list is treated as one piece of content.
    additional_instructions: Additional instructions for the language model.
    language_model: The language model to use. Defaults to a Gemini LLM.

  Returns:
    A list of IABCategory objects representing the assigned categories.
  """
  content_key_value = KeyValue("keyword", iab.create_content_taxonomy())
  audience_key_value = KeyValue(
      "expected_audience", iab.create_audience_taxonomy()
  )
  response_dict = generate_key_values(
      content,
      [content_key_value, audience_key_value],
      additional_instructions,
      language_model,
  )
  return response_dict["keyword"] + response_dict["expected_audience"]


def add_ai_attributes_to_video(
    video: video_class.Video,
    audio_bucket_name: str = project_configs.AUDIO_BUCKET_NAME,
) -> video_class.Video:
  """Enhances a Video object with AI-generated attributes.

  This function performs the following steps:
  1. Retrieves the transcript of the video (creating one, if necessary).
  2. Checks if the transcript length is sufficient and the video duration is
    below a threshold.
  3. Generates and assigns a summary of the video using an AI model.
  4. Generates and assigns AI-generated metadata for the video.
  5. Generates and assigns AI-suggested titles for the video.
  6. Generates and assigns an AI-suggested external summary for the video.

  Args:
    video: The Video object to be enhanced with AI-generated attributes.
    audio_bucket_name: The name of the bucker in Google Cloud Storage where
      extracted audio files should be stored.

  Returns:
    The video instance with additional AI attributes.

  Raises:
    IOError: If there is an issue with retrieving or processing the transcript.
  """
  transcript = (
      video.transcript
      or transcription_utils.get_transcript_from_video(video, audio_bucket_name)
  )
  video_copy = copy.deepcopy(video)
  video_copy.transcript = transcript
  # If the transcript is not long enough (<100 characters), or
  # the video is too long (> 40 minutes), do not proceed with genAI.
  if len(transcript) > 100 and video.detect_duration() < 2400:
    llm = models.create_gemini_llm()
    video_copy.summary = describe(
        f"Content Transcript: {video.transcript}", language_model=llm
    )
    video_copy.ai_generated_metadata = generate_metadata(
        [
            f"Title: {video.title}",
            f"Transcript: {video.transcript}",
            f"Summary: {video.summary}",
        ],
        language_model=llm,
    )
    video_copy.ai_suggested_titles = suggest_titles(
        [
            f"Title: {video.title}",
            f"Transcript: {video.transcript}",
            f"Summary: {video.summary}",
        ],
        language_model=llm,
    )
    video_copy.ai_suggested_external_summary = summarize(
        [
            f"Title: {video.title}",
            f"Transcript: {video.transcript}",
            f"Summary: {video.summary}",
        ],
        language_model=llm,
    )
  return video_copy


def _parse_args(args: Sequence[str]) -> argparse.Namespace:
  """Parses command line arguments for ai_metadata_generator.

  Args:
    args: The command line arguments.

  Returns:
    The parsed arguments.
  """

  argparser = argparse.ArgumentParser(
      description="Analyzes content using AI.",
      formatter_class=argparse.RawTextHelpFormatter,
  )
  argparser.add_argument(
      "action",
      choices=["describe", "summarize", "tag", "title", "iab"],
      help=(
          "The action to perform for the provided content. Valid actions are:\n"
          "  title: suggests possible titles for the content\n  describe:"
          " describes the content with as much detail as possible\n  summarize:"
          " summarizes the content for an external audience\n  tag: identifies"
          " keywords related to the content (use with --keys to specify custom"
          " keys)\n  iab: identifies IAB content and audience categories"
          " related to the content"
      ),
  )
  argparser.add_argument(
      "--keys",
      nargs="+",
      type=str,
      help=(
          'Use with "tag" to create key/values instead of free-form'
          " metadata values. No-op otherwise."
      ),
  )
  argparser.add_argument(
      "content_file",
      type=str,
      help="The URI of the content to be processed (local files only).",
  )
  argparser.add_argument(
      "--vertex",
      "-v",
      action="store_true",
      help=(
          "Use Vertex AI. Requires Application Default Credentials with a"
          " default project to be configured."
      ),
  )
  return argparser.parse_args(args)


def main(args=sys.argv[1:]):
  """Entry point for command line interface.

  Args:
    args: The command line arguments. Provided by default, but can be passed
      manually to enable easier testing.
  """
  arguments = _parse_args(args)
  action = arguments.action
  content_path = arguments.content_file

  gemini = (
      models.create_gemini_llm_with_vertex()
      if arguments.vertex
      else models.create_gemini_llm()
  )
  content_file = file_io.File(content_path)
  match action:
    case "title":
      preamble = "Suggested Titles"
      result = suggest_titles(content_file, language_model=gemini)
    case "summarize":
      preamble = "Suggested Content Summary"
      result = summarize(content_file, language_model=gemini)
    case "tag":
      if arguments.keys:
        preamble = "Suggested Key Values"
        result = generate_key_values(
            content_file, arguments.keys, language_model=gemini
        )
      else:
        preamble = "Suggested Metadata"
        result = generate_metadata(content_file, language_model=gemini)
    case "iab":
      preamble = "Suggested IAB Categories"
      categories = generate_iab_categories(content_file, language_model=gemini)
      result = f"{'Taxonomy':<20}{'ID':>7}  {'Category'}\n" + "\n".join([
          f"{category.taxonomy_name:<20}{category.unique_id:>7} "
          f" {category.name}"
          for category in categories
      ])
    case _:
      # argparse should make this impossible
      raise ValueError("Unexpected action specified.")

  content_file.cleanup()
  print(f"{preamble} ({content_path}):")
  print(result)


if __name__ == "__main__":
  main()
