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
"""Test the ai metadata genertator file."""

import unittest
from unittest import mock

import ai_metadata_generator
import models
import transcription_utils
import video_class


class TestAIMetadataGenerator(unittest.TestCase):

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_suggest_titles_returns_titles(self, mock_create_gemini_llm):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = '["Title 1", "Title 2"]'

    titles = ai_metadata_generator.suggest_titles(
        "text content", language_model=mock_llm
    )

    self.assertEqual(titles, ["Title 1", "Title 2"])

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_suggest_titles_prompts_with_content(self, mock_create_gemini_llm):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = '["Title 1", "Title 2"]'

    ai_metadata_generator.suggest_titles(
        "text content", language_model=mock_llm
    )

    mock_llm.generate.assert_called_once_with(
        [
            "text content",
            (
                "You are a creative and experienced headline/title generator"
                " for a leading\nmedia company. You specialize in crafting"
                " compelling and engaging titles for\na variety of content,"
                " including video content and text articles. Your goal\nis to"
                " help content editors create titles that attract"
                " readers/viewers,\naccurately reflect the content, and drive"
                " engagement.\n\nKey Responsibilities:\n- Understand the"
                " nuances of different content types: You can"
                " differentiate\nbetween titles for videos and articles and"
                " tailor your suggestions\naccordingly.\n- Generate multiple"
                " title options: You will offer a diverse range of"
                " title\nsuggestions based on the provided context.\n- Adapt to"
                " different tones and styles: You can adjust the tone of the"
                " title\nto match the content, whether it's serious, humorous,"
                " informative, or\nsensational.\n- The title should clearly"
                " convey the main topic or theme of the content.\n- The title"
                " should pique the reader's/viewer's curiosity and encourage"
                " them\nto click.\n- The title should accurately reflect the"
                " content and avoid misleading or\nclickbait tactics.\n- Keep"
                " titles concise and to the point where possible, but"
                " prioritize\nclarity and impact over arbitrary length"
                " limits.\n"
            ),
        ],
        list[str],
        1.2,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_suggest_titles_prompts_with_additional_instructions(
      self, mock_create_gemini_llm
  ):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = '["Title 1", "Title 2"]'

    ai_metadata_generator.suggest_titles(
        "text content", "user instructions", language_model=mock_llm
    )

    mock_llm.generate.assert_called_once_with(
        [
            "text content",
            (
                "You are a creative and experienced headline/title generator"
                " for a leading\nmedia company. You specialize in crafting"
                " compelling and engaging titles for\na variety of content,"
                " including video content and text articles. Your goal\nis to"
                " help content editors create titles that attract"
                " readers/viewers,\naccurately reflect the content, and drive"
                " engagement.\n\nKey Responsibilities:\n- Understand the"
                " nuances of different content types: You can"
                " differentiate\nbetween titles for videos and articles and"
                " tailor your suggestions\naccordingly.\n- Generate multiple"
                " title options: You will offer a diverse range of"
                " title\nsuggestions based on the provided context.\n- Adapt to"
                " different tones and styles: You can adjust the tone of the"
                " title\nto match the content, whether it's serious, humorous,"
                " informative, or\nsensational.\n- The title should clearly"
                " convey the main topic or theme of the content.\n- The title"
                " should pique the reader's/viewer's curiosity and encourage"
                " them\nto click.\n- The title should accurately reflect the"
                " content and avoid misleading or\nclickbait tactics.\n- Keep"
                " titles concise and to the point where possible, but"
                " prioritize\nclarity and impact over arbitrary length"
                " limits.\n"
            ),
            "**Additional Instructions:** user instructions",
        ],
        list[str],
        1.2,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_describe_returns_description(self, mock_create_gemini_llm):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = "long description..."

    titles = ai_metadata_generator.describe(
        "text content", language_model=mock_llm
    )

    self.assertEqual(titles, "long description...")

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_describe_prompts_with_content(self, mock_create_gemini_llm):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = "long description..."

    ai_metadata_generator.describe("text content", language_model=mock_llm)

    mock_llm.generate.assert_called_once_with(
        [
            "text content",
            (
                "You are a Content Analyst for a major media company. Your role"
                " is to\nthoroughly analyze and describe various media content,"
                " including videos,\nimages, and articles. Your descriptions"
                " should be detailed, accurate, and\nwritten in complete,"
                " grammatically correct sentences.\n\nKey Responsibilities:\n-"
                " Describe the content in detail:  Provide a comprehensive"
                " description of\nwhat is shown or written in the content."
                " Include relevant details such as:\n  * For videos: Setting,"
                " characters, actions, dialogue (if clear and\n  relevant),"
                " overall narrative or message, and any notable visual or\n "
                " auditory elements.\n  * For images: Subject, composition,"
                " colors, lighting, style, and any\n  discernible context or"
                " message.\n  * For articles: Topic, main points, arguments,"
                " tone, writing style, and\n  intended audience.\n- Be"
                " objective: Focus on describing what is present in the content"
                " without\nadding personal opinions or interpretations.\n- Be"
                " thorough:  Aim for a detailed description that captures the"
                " essence\nof the content.\n- Use precise language: Choose"
                " words carefully to accurately convey the\ndetails of the"
                " content.\n\nYour analysis is crucial for content cataloging,"
                " searchability, and\nunderstanding the company's media"
                " assets.\n"
            ),
        ],
        str,
        1.2,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_describe_prompts_with_additional_instructions(
      self, mock_create_gemini_llm
  ):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = "long description..."

    ai_metadata_generator.describe(
        "text content", "user instructions", language_model=mock_llm
    )

    mock_llm.generate.assert_called_once_with(
        [
            "text content",
            (
                "You are a Content Analyst for a major media company. Your role"
                " is to\nthoroughly analyze and describe various media content,"
                " including videos,\nimages, and articles. Your descriptions"
                " should be detailed, accurate, and\nwritten in complete,"
                " grammatically correct sentences.\n\nKey Responsibilities:\n-"
                " Describe the content in detail:  Provide a comprehensive"
                " description of\nwhat is shown or written in the content."
                " Include relevant details such as:\n  * For videos: Setting,"
                " characters, actions, dialogue (if clear and\n  relevant),"
                " overall narrative or message, and any notable visual or\n "
                " auditory elements.\n  * For images: Subject, composition,"
                " colors, lighting, style, and any\n  discernible context or"
                " message.\n  * For articles: Topic, main points, arguments,"
                " tone, writing style, and\n  intended audience.\n- Be"
                " objective: Focus on describing what is present in the content"
                " without\nadding personal opinions or interpretations.\n- Be"
                " thorough:  Aim for a detailed description that captures the"
                " essence\nof the content.\n- Use precise language: Choose"
                " words carefully to accurately convey the\ndetails of the"
                " content.\n\nYour analysis is crucial for content cataloging,"
                " searchability, and\nunderstanding the company's media"
                " assets.\n"
            ),
            "**Additional Instructions:** user instructions",
        ],
        str,
        1.2,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_summarize_returns_summary(self, mock_create_gemini_llm):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = "summary..."

    summary = ai_metadata_generator.summarize(
        "text content", language_model=mock_llm
    )

    self.assertEqual(summary, "summary...")

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_summarize_prompts_with_content(self, mock_create_gemini_llm):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = "summary..."

    ai_metadata_generator.summarize("text content", language_model=mock_llm)

    mock_llm.generate.assert_called_once_with(
        [
            "text content",
            (
                "You are a highly skilled content summarization agent working"
                " for a media\ncompany. Your primary function is to create"
                " engaging and informative\nsummaries for various types of"
                " media content, including movies, TV shows,\ndocumentaries,"
                " and short-form videos. These summaries will be used in"
                " a\ncontent library and potentially displayed on a streaming"
                " service platform.\nYour summaries should cater to a general"
                " audience and entice viewers to\nwatch the full"
                " content.\n\nKey Responsibilities:\n- Generate concise and"
                " captivating summaries: Focus on the core plot,"
                " key\ncharacters, and unique selling points of the content."
                " Avoid spoilers and\nmaintain a neutral tone, unless otherwise"
                " specified.\n- Understand target audience: Write for a general"
                " audience unless specific\ndemographic information is"
                " provided. Assume the audience is interested in\ndiscovering"
                " new content but may not be familiar with the specific"
                " title.\n- Maintain a consistent style and tone: Use clear,"
                " concise language, and\navoid jargon or overly technical"
                " terms. Strive for a professional yet\nengaging tone that"
                " sparks interest.\n- Prioritize accuracy and avoid"
                " speculation: Base your summaries solely on\nthe provided"
                " information (e.g., transcripts, plot outlines,"
                " existing\ndescriptions). Do not invent plot details or"
                " speculate about character\nmotivations.\n\nOutput format:"
                " Format your summaries as plain text.\n"
            ),
        ],
        str,
        1.2,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_summarize_prompts_with_additional_instructions(
      self, mock_create_gemini_llm
  ):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = "summary..."

    ai_metadata_generator.summarize(
        "text content", "user instructions", language_model=mock_llm
    )

    mock_llm.generate.assert_called_once_with(
        [
            "text content",
            (
                "You are a highly skilled content summarization agent working"
                " for a media\ncompany. Your primary function is to create"
                " engaging and informative\nsummaries for various types of"
                " media content, including movies, TV shows,\ndocumentaries,"
                " and short-form videos. These summaries will be used in"
                " a\ncontent library and potentially displayed on a streaming"
                " service platform.\nYour summaries should cater to a general"
                " audience and entice viewers to\nwatch the full"
                " content.\n\nKey Responsibilities:\n- Generate concise and"
                " captivating summaries: Focus on the core plot,"
                " key\ncharacters, and unique selling points of the content."
                " Avoid spoilers and\nmaintain a neutral tone, unless otherwise"
                " specified.\n- Understand target audience: Write for a general"
                " audience unless specific\ndemographic information is"
                " provided. Assume the audience is interested in\ndiscovering"
                " new content but may not be familiar with the specific"
                " title.\n- Maintain a consistent style and tone: Use clear,"
                " concise language, and\navoid jargon or overly technical"
                " terms. Strive for a professional yet\nengaging tone that"
                " sparks interest.\n- Prioritize accuracy and avoid"
                " speculation: Base your summaries solely on\nthe provided"
                " information (e.g., transcripts, plot outlines,"
                " existing\ndescriptions). Do not invent plot details or"
                " speculate about character\nmotivations.\n\nOutput format:"
                " Format your summaries as plain text.\n"
            ),
            "**Additional Instructions:** user instructions",
        ],
        str,
        1.2,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_generate_key_values_returns_key_values(self, mock_create_gemini_llm):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = '{"keyword": ["tag1", "tag2"]}'

    key_values = ai_metadata_generator.generate_key_values(
        "text content", ["keyword"], language_model=mock_llm
    )

    self.assertEqual(key_values, {"keyword": ["tag1", "tag2"]})

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_generate_key_values_prompts_with_content(
      self, mock_create_gemini_llm
  ):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = '{"keyword": ["tag1", "tag2"]}'

    ai_metadata_generator.generate_key_values(
        "text content", ["keyword"], language_model=mock_llm
    )

    mock_llm.generate.assert_called_once_with(
        [
            "text content",
            (
                "You are a highly skilled Content Editor working for a major"
                " media company.\nYour role involves a deep understanding of"
                " content analysis, metadata\nstandards, and SEO principles."
                " Your current task is focused on enhancing"
                " the\ndiscoverability of our content library (videos, images,"
                " and articles)\nthrough effective metadata tagging.\n\nKey"
                " Responsibilities:\n- Content Analysis: Carefully review the"
                " provided content (video content,\nimages, or full articles)"
                " and identify its core topics, themes, and key\nelements.\n-"
                " Metadata Tag Generation: Generate a comprehensive set of"
                " metadata tags\nthat accurately describe the content.\n-"
                " Prioritize Accuracy: Ensure tags are factual and directly"
                " related to the\ncontent.\n- Include a range of tags"
                " covering:\n  * Descriptive: What is literally depicted or"
                " discussed?\n  * Conceptual: What are the underlying themes"
                " and ideas?\n  * Categorical:  What broader categories does"
                " the content belong to?\n  * Named Entities: Are there"
                " specific people, places, organizations, or\n  events"
                " featured?\n  * SEO Optimization: Where appropriate, consider"
                " relevant keywords and\n  search trends to improve content"
                " discoverability.\n"
            ),
        ],
        {
            "type": "object",
            "properties": {
                "keyword": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["keyword"],
        },
        0.6,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_generate_key_values_prompts_with_additional_instructions(
      self, mock_create_gemini_llm
  ):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = '{"keyword": ["tag1", "tag2"]}'

    ai_metadata_generator.generate_key_values(
        "text content",
        ["keyword"],
        "user instructions",
        language_model=mock_llm,
    )

    mock_llm.generate.assert_called_once_with(
        [
            "text content",
            (
                "You are a highly skilled Content Editor working for a major"
                " media company.\nYour role involves a deep understanding of"
                " content analysis, metadata\nstandards, and SEO principles."
                " Your current task is focused on enhancing"
                " the\ndiscoverability of our content library (videos, images,"
                " and articles)\nthrough effective metadata tagging.\n\nKey"
                " Responsibilities:\n- Content Analysis: Carefully review the"
                " provided content (video content,\nimages, or full articles)"
                " and identify its core topics, themes, and key\nelements.\n-"
                " Metadata Tag Generation: Generate a comprehensive set of"
                " metadata tags\nthat accurately describe the content.\n-"
                " Prioritize Accuracy: Ensure tags are factual and directly"
                " related to the\ncontent.\n- Include a range of tags"
                " covering:\n  * Descriptive: What is literally depicted or"
                " discussed?\n  * Conceptual: What are the underlying themes"
                " and ideas?\n  * Categorical:  What broader categories does"
                " the content belong to?\n  * Named Entities: Are there"
                " specific people, places, organizations, or\n  events"
                " featured?\n  * SEO Optimization: Where appropriate, consider"
                " relevant keywords and\n  search trends to improve content"
                " discoverability.\n"
            ),
            "**Additional Instructions:** user instructions",
        ],
        {
            "type": "object",
            "properties": {
                "keyword": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["keyword"],
        },
        0.6,
    )

  @mock.patch.object(
      ai_metadata_generator, "generate_key_values", autospec=True
  )
  def test_generate_metadata_uses_generate_key_values(
      self, mock_generate_key_values
  ):
    mock_generate_key_values.return_value = {"keyword": ["tag1", "tag2"]}

    metadata = ai_metadata_generator.generate_metadata(
        "any content", "additional instructions", None
    )

    self.assertEqual(metadata, ["tag1", "tag2"])
    mock_generate_key_values.assert_called_once_with(
        "any content", ["keyword"], "additional instructions", None
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  @mock.patch.object(
      transcription_utils, "get_transcript_from_video", autospec=True
  )
  @mock.patch.object(ai_metadata_generator, "describe", autospec=True)
  @mock.patch.object(ai_metadata_generator, "generate_metadata", autospec=True)
  @mock.patch.object(ai_metadata_generator, "summarize", autospec=True)
  @mock.patch.object(ai_metadata_generator, "suggest_titles", autospec=True)
  def test_add_ai_attributes_to_video(
      self,
      mock_suggest_titles,
      mock_summarize,
      mock_generate_metadata,
      mock_describe,
      mock_get_transcript_from_video,
      _,
  ):
    """Tests adding ai attributes to a video (e.g. metadata/summary/titles)."""
    transcript = (
        "This is a long transcript with more than 100 characters. This ensures"
        " the transcription length condition is satisfied."
    )
    mock_get_transcript_from_video.return_value = transcript
    video = video_class.Video(
        video_id="1234", uri="https://example.com/video.mp4", duration=1200
    )
    audio_bucket_name = "audio_bucket"
    mock_suggest_titles.return_value = ["Title 1", "Title 2"]
    mock_summarize.return_value = "Generated external summary"
    mock_generate_metadata.return_value = ["tag1", "tag2"]
    mock_describe.return_value = "Generated summary"

    video = ai_metadata_generator.add_ai_attributes_to_video(
        video, audio_bucket_name
    )

    self.assertEqual(
        video.transcript,
        transcript,
    )
    self.assertEqual(video.summary, "Generated summary")
    self.assertEqual(video.ai_generated_metadata, ["tag1", "tag2"])
    self.assertEqual(video.ai_suggested_titles, ["Title 1", "Title 2"])
    self.assertEqual(
        video.ai_suggested_external_summary, "Generated external summary"
    )


if __name__ == "__main__":
  unittest.main()
