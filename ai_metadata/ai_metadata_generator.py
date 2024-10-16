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
artificial intelligence to generate metadata related to the content. Depending
on the input data, this module can generate transcripts, descriptions,
summaries, keyword metadata, title suggestions, and external summaries.

Most of the generated content requires a transcript so if there is not one
provided it will be generated.

usage: ai_metadata_generator.py [-h] [--video_id VIDEO_ID] [--title TITLE]
  [--metadata METADATA] video_uri

positional arguments:
  video_uri            The URI of the video to be processed.

options:
  -h, --help           show this help message and exit
  --video_id VIDEO_ID  The unique identifier of the video. If not provided,
                        it will be extracted from the video URI.
  --title TITLE        User provided title for the video. Defaults to an
                        empty string
  --metadata METADATA  User provided metadata associated with the video.
                        Defaults to anempty string.
"""

import argparse
import copy
import string
import sys
from typing import Sequence

import llm_utils
import project_configs
import transcription_utils
import video_class


def _create_video_id_from_uri(uri: str):
  """Replaces punctuation in a URI with underscores to create an ID."""
  chars_to_replace = string.punctuation + " "
  translator = str.maketrans(
      string.punctuation + " ", "_" * len(chars_to_replace)
  )
  return uri.translate(translator)


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
  if not video.transcript:
    video.transcript = transcription_utils.get_transcript_from_video(
        video,
        audio_bucket_name,
    )

  video_copy = copy.deepcopy(video)
  # If the transcript is not long enough (<100 characters), or
  # the video is too long (> 40 minutes), do not proceed with genAI.
  if len(video.transcript) > 100 and video.detect_duration() < 2400:
    video_copy.summary = llm_utils.call_llm(video_copy, "generate_summary")
    video_copy.ai_generated_metadata = llm_utils.call_llm(
        video_copy, "generate_metadata"
    )
    video_copy.ai_suggested_titles = llm_utils.call_llm(
        video_copy, "generate_title_options"
    )
    video_copy.ai_suggested_external_summary = llm_utils.call_llm(
        video_copy, "generate_external_summary"
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
      description="Describes video content using AI."
  )
  argparser.add_argument(
      "video_uri",
      type=str,
      help="The URI of the video to be processed.",
  )
  argparser.add_argument(
      "--video_id",
      type=str,
      default=None,
      help=(
          "The unique identifier of the video. If not provided, it will be"
          "extracted from the video URI."
      ),
  )
  argparser.add_argument(
      "--title",
      type=str,
      default="",
      help="User provided title for the video. Defaults to an empty string",
  )
  argparser.add_argument(
      "--metadata",
      type=str,
      default="",
      help=(
          "User provided metadata associated with the video. Defaults to an"
          "empty string."
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
  if not arguments.video_uri:
    raise ValueError("No video URL specified.")

  video_id = arguments.video_id or _create_video_id_from_uri(
      arguments.video_uri
  )
  video = video_class.Video(
      video_id,
      uri=arguments.video_uri,
      metadata=arguments.metadata,
      title=arguments.title,
  )
  video = add_ai_attributes_to_video(
      video,
      project_configs.AUDIO_BUCKET_NAME,
  )
  print(f"AI Generated Metadata:\n{video.ai_generated_metadata}")


if __name__ == "__main__":
  main()
