"""Command-line interface for AI metadata generation and ad cue point detection.

This module provides a script to analyze video content using AI models for tasks
such as title suggestion, summarization, tagging, IAB categorization, and
identifying optimal ad cue points.
"""

import argparse
import sys
from typing import Sequence
from ai_metadata import ai_metadata_generator
from ai_metadata import file_io
from ai_metadata import models
from google.cloud import videointelligence
from smart_ad_breaks import cue_point_generator
from smart_ad_breaks import video_analysis


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
      choices=["describe", "summarize", "tag", "title", "iab", "cues"],
      help=(
          "The action to perform for the provided content. Valid actions are:\n"
          "  title: suggests possible titles for the content\n  describe:"
          " describes the content with as much detail as possible\n  summarize:"
          " summarizes the content for an external audience\n  tag: identifies"
          " keywords related to the content (use with --keys to specify custom"
          " keys)\n  iab: identifies IAB content and audience categories"
          " related to the content\n  cues: identifies suitable ad cue point"
          " placement for video content"
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
      "--first_cue",
      "-f",
      type=float,
      default=0.0,
      help=(
          'Use with "cues" to specify the earliest time that a cue point should'
          'be created. Defaults to "0.0."'
      ),
  )
  argparser.add_argument(
      "--between_cues",
      "-b",
      type=float,
      default=30.0,
      help=(
          'Use with "cues" to specify the minimum amount of time that should be'
          " between two cue points. Defaults to 30.0."
      ),
  )
  argparser.add_argument(
      "--volume_threshold",
      "-v",
      type=float,
      default=None,
      help=(
          'Use with "cues." If provided, the maximum in volume, in dB, for a'
          " cue point. This is always a no-op for files hosted on GCP."
      ),
  )
  argparser.add_argument(
      "content_file",
      type=str,
      help=(
          "The URI of the content to be processed. Files hosted on GCS should"
          " use the prefix gs:// and require Application Default Credentials"
          " with a default project to be configured."
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

  is_gcs_file = content_path.startswith("gs://")

  # smart_ad_breaks
  if action == "cues":
    if is_gcs_file:
      video_intel_client = videointelligence.VideoIntelligenceServiceClient()
      video_analyzer = video_analysis.CloudVideoAnalyzer(video_intel_client)
    else:
      video_analyzer = video_analysis.FfmpegVideoAnalyzer()
    cue_points = cue_point_generator.determine_video_cue_points(
        arguments.content_file,
        video_analyzer,
        minimum_time_for_first_cue_point=arguments.first_cue,
        minimum_time_between_cue_points=arguments.between_cues,
        volume_threshold=arguments.volume_threshold,
    )
    print("Recommended cue points: ", cue_points)
    return

  # ai_metadata
  gemini = (
      models.create_gemini_llm_with_vertex()
      if is_gcs_file
      else models.create_gemini_llm()
  )
  content_file = file_io.File(content_path)
  match action:
    case "title":
      preamble = "Suggested Titles"
      result = ai_metadata_generator.suggest_titles(
          content_file, language_model=gemini
      )
    case "summarize":
      preamble = "Suggested Content Summary"
      result = ai_metadata_generator.summarize(
          content_file, language_model=gemini
      )
    case "tag":
      if arguments.keys:
        preamble = "Suggested Key Values"
        result = ai_metadata_generator.generate_key_values(
            content_file, arguments.keys, language_model=gemini
        )
      else:
        preamble = "Suggested Metadata"
        result = ai_metadata_generator.generate_metadata(
            content_file, language_model=gemini
        )
    case "iab":
      preamble = "Suggested IAB Categories"
      categories = ai_metadata_generator.generate_iab_categories(
          content_file, language_model=gemini
      )
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
