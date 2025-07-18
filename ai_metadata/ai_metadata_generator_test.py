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

from ai_metadata import ai_metadata_generator
from ai_metadata import iab
from ai_metadata import models


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
                "You are a highly skilled Ad Targeting Specialist responsible"
                " for maximizing theadvertising revenue potential of multimedia"
                " content. Your task is to accurately assign values to a set of"
                " keys, selecting from provided lists when\navailable, and"
                " generating relevant values when lists are not provided. Your"
                " primary goal is to choose values that are highly relevant to"
                " potential advertisers.\n\n**Keys and Allowed Values (if"
                " applicable):**\n\nKey: keyword\n "
                " Any\n\n**Instructions:**\n\n1. **Carefully review the input"
                " content.** Understand its core topics, themes, and key"
                " elements *in the context of potential advertising*.\n2. **For"
                " *each* key, follow these rules:**\n  - **If Allowed Values"
                " are provided:** Select the most relevant values *from an"
                " advertising perspective* from the corresponding list."
                " Prioritize values that are likely to be used as keywords by"
                " advertisers targeting this type of content. Do *not* generate"
                " any values outside of the provided list.\n  - **If Allowed"
                " Values are *not* provided (the key is listed, but the only"
                ' value is "Any"):** Generate values that are highly relevant'
                " to advertisers. Consider:\n    - **Common Advertising"
                ' Categories:** Think about categories like "Travel,"'
                ' "Technology," "Food & Beverage," "Finance," "Automotive,"'
                ' "Fashion," etc., and how the video content might relate.\n   '
                " - **Target Audience Interests:**  Align your generated values"
                " with the interests and demographics of the most likely target"
                " audience.\n    - **Keywords:** Use terms that advertisers"
                " would likely use to target this content.\n3. **Strict"
                " Adherence (for keys with Allowed Values):** When allowed"
                " values *are* provided, it is *critical* that you *only* use"
                " the exact values from the list. Do not modify, rephrase, or"
                " add any words. Copy the allowed values *exactly* as they"
                " appear.  Prioritize advertising relevance when selecting.\n"
            ),
        ],
        {
            "type": "object",
            "properties": {
                "keyword": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["keyword"],
        },
        0.0,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_generate_key_values_prompts_with_additional_instructions(
      self, mock_create_gemini_llm
  ):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = '{"keyword": ["tag1", "tag2"]}'

    ai_metadata_generator.generate_key_values(
        [
            "text content",
            (
                "You are a highly skilled Ad Targeting Specialist responsible"
                " for maximizing theadvertising revenue potential of multimedia"
                " content. Your task is to accurately assign values to a set of"
                " keys, selecting from provided lists when\navailable, and"
                " generating relevant values when lists are not provided. Your"
                " primary goal is to choose values that are highly relevant to"
                " potential advertisers.\n\n**Keys and Allowed Values (if"
                " applicable):**\n\nKey: keyword\n "
                " Any\n\n**Instructions:**\n\n1. **Carefully review the input"
                " content.** Understand its core topics, themes, and key"
                " elements *in the context of potential advertising*.\n2. **For"
                " *each* key, follow these rules:**\n  - **If Allowed Values"
                " are provided:** Select the most relevant values *from an"
                " advertising perspective* from the corresponding list."
                " Prioritize values that are likely to be used as keywords by"
                " advertisers targeting this type of content. Do *not* generate"
                " any values outside of the provided list.\n  - **If Allowed"
                " Values are *not* provided (the key is listed, but the only"
                ' value is "Any"):** Generate values that are highly relevant'
                " to advertisers. Consider:\n    - **Common Advertising"
                ' Categories:** Think about categories like "Travel,"'
                ' "Technology," "Food & Beverage," "Finance," "Automotive,"'
                ' "Fashion," etc., and how the video content might relate.\n   '
                " - **Target Audience Interests:**  Align your generated values"
                " with the interests and demographics of the most likely target"
                " audience.\n    - **Keywords:** Use terms that advertisers"
                " would likely use to target this content.\n3. **Strict"
                " Adherence (for keys with Allowed Values):** When allowed"
                " values *are* provided, it is *critical* that you *only* use"
                " the exact values from the list. Do not modify, rephrase, or"
                " add any words. Copy the allowed values *exactly* as they"
                " appear.  Prioritize advertising relevance when selecting.\n"
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
        0.0,
    )

  @mock.patch.object(models, "create_gemini_llm", autospec=True)
  def test_generate_key_values_from_list(self, mock_create_gemini_llm):
    mock_llm = mock_create_gemini_llm.return_value
    mock_llm.generate.return_value = (
        '{"keyword": ["tag1", "tag2"], "keyword2": ["tag1", "tag3", "tag4"]}'
    )

    predefined_key = ai_metadata_generator.KeyValue(
        "keyword2", ["tag1", "tag2"]
    )
    ai_metadata_generator.generate_key_values(
        "text content",
        ["keyword", predefined_key],
        "user instructions",
        language_model=mock_llm,
    )

    expected_allowed_values_str = (
        "**Keys and Allowed Values (if applicable):**\n\nKey: keyword\n "
        " Any\n\nKey: keyword2\n  tag1\n  tag2\n\n"
    )

    prompt, schema, temperature = mock_llm.generate.call_args.args
    self.assertTrue(
        any([
            expected_allowed_values_str in prompt_part for prompt_part in prompt
        ])
    )
    self.assertEqual(
        schema,
        {
            "type": "object",
            "properties": {
                "keyword": {"type": "array", "items": {"type": "string"}},
                "keyword2": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["keyword", "keyword2"],
        },
    )
    self.assertEqual(temperature, 0.0)

  @mock.patch.object(
      ai_metadata_generator, "generate_key_values", autospec=True
  )
  def test_generate_metadata_uses_generate_key_values(
      self, mock_generate_key_values
  ):
    mock_generate_key_values.return_value = {"keyword": ["tag1", "tag2"]}

    metadata = ai_metadata_generator.generate_metadata(
        "any content", None, "additional instructions", None
    )

    self.assertEqual(metadata, ["tag1", "tag2"])
    mock_generate_key_values.assert_called_once_with(
        "any content",
        [ai_metadata_generator.KeyValue("keyword", [])],
        "additional instructions",
        None,
    )

  @mock.patch.object(iab, "create_content_taxonomy", autospec=True)
  @mock.patch.object(iab, "create_audience_taxonomy", autospec=True)
  @mock.patch.object(
      ai_metadata_generator, "generate_key_values", autospec=True
  )
  def test_generate_iab_categories_calls_generate_key_values(
      self,
      mock_generate_key_values,
      mock_create_audience_taxonomy,
      mock_create_content_taxonomy,
  ):
    ai_metadata_generator.generate_iab_categories(
        "content", additional_instructions="additional"
    )

    mock_generate_key_values.assert_called_once_with(
        "content",
        [
            ai_metadata_generator.KeyValue(
                "keyword",
                allowed_values=mock_create_content_taxonomy.return_value,
            ),
            ai_metadata_generator.KeyValue(
                "expected_audience",
                allowed_values=mock_create_audience_taxonomy.return_value,
            ),
        ],
        "additional",
        None,
    )

  @mock.patch.object(iab, "create_content_taxonomy", autospec=True)
  @mock.patch.object(iab, "create_audience_taxonomy", autospec=True)
  @mock.patch.object(
      ai_metadata_generator, "generate_key_values", autospec=True
  )
  def test_generate_iab_categories_parses_generate_key_values_responses(
      self,
      mock_generate_key_values,
      *_,
  ):
    mock_generate_key_values.return_value = {
        "keyword": [
            iab.TaxonomyEntity("content", "0", "tag1"),
            iab.TaxonomyEntity("content", "2", "tag3"),
        ],
        "expected_audience": [iab.TaxonomyEntity("audience", "1", "audience2")],
    }

    entities = ai_metadata_generator.generate_iab_categories("content")

    self.assertEqual(
        entities,
        [
            iab.TaxonomyEntity("content", "0", "tag1"),
            iab.TaxonomyEntity("content", "2", "tag3"),
            iab.TaxonomyEntity("audience", "1", "audience2"),
        ],
    )


if __name__ == "__main__":
  unittest.main()
