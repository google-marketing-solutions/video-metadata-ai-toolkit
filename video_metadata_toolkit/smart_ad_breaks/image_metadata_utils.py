#!/usr/bin/env python

# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module is responsible for helper functions used in metadata generation.

This code is meant to provide helper functions common to both VOD and Live
metadata generation scripts.
"""

import os

import ffmpeg
from google.cloud import vision


def detect_labels_dict(
    path: str,
    in_dict: dict[str, int],
    threshold: float,
) -> dict[str, int]:
  """Gets labels and saves in dictionary from given screenshot image

  using Cloud Vision API.

  Args:
      path: A string of the path of the screenshot to be processed.
      in_dict: An empty or existing dict where the key is the string of labels,
        and the values are the frequency of appearance of each.
      threshold: A float representing the threshold to use for label detection.

  Returns:
      A dict mapping where keys are string labels related to metadata
      of each print and their int frequency of appeareance in descending order.

      For example:
        {
         "Wood": 6,
         "Audio equipment": 1,
         "Handwriting": 1,
         "Technology": 1
        }
  """
  client = vision.ImageAnnotatorClient()

  with open(path, "rb") as image_file:
    content = image_file.read()

  image = vision.Image(content=content)

  response = client.label_detection(image=image)
  labels = response.label_annotations
  thresholdf = float(threshold)

  for label in labels:
    if label.score >= thresholdf:
      label_freq = in_dict.get(label.description, 0)
      in_dict[label.description] = label_freq + 1

  return in_dict


def generate_screenshot(
    in_filename: str,
    out_filename: str,
    time: int,
    width: int,
) -> str:
  """Gets a screenshot at specific time frame and saves locally.

  Args:
      in_filename: The path of the .mp4 video file to be processed.
      out_filename: The path where the screenshot should be saved. Add desired
        extesion.
      time: An int of the time in seconds of where to take the printscreen from
        video.
      width: An int representing the desired size of screenshot. Example: 500.

  Returns:
      A string of the generated screenshot file name.

  Raises:
      ffmpeg.Error: An error during screenshot generation process.
  """

  try:
    (
        ffmpeg.input(in_filename, ss=time)
        .filter("scale", width, -1)
        .output(out_filename, vframes=1)
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
  except ffmpeg.Error as e:
    print(f"Error genetaing screenshot: {e.stderr.decode()}")
    raise e from None

  return out_filename


def get_video_duration(in_filename: str) -> int:
  """Gets a video file duration.

  Args:
      in_filename: A string of the path of the video file to be processed.

  Returns:
      An int of the video duration in seconds.
  """

  duration = ffmpeg.probe(in_filename)["format"]["duration"]
  return duration


def remove_local_file(in_file: str) -> str:
  """Removes a local file.

  Args:
      in_file: A string of the file to be removed.

  Returns:
      A string of the file path/name removed.
  """

  os.remove(in_file)
  return str
