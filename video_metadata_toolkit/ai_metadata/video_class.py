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

import shlex
import subprocess


class Video:
  """Represents a video, storing its metadata and  AI-generated metadata.

  video_id: Unique identifier for the video.
  uri: The URI where the video is located.
  title: The title of the video.
  description: A description of the video.
  metadata: Additional metadata associated with the video.
  transcript: A transcription of the video's audio.
  summary: A concise summary of the video's content.
  languages: A list of languages associated with the content.
  duration: The duration of the video in seconds.
  ai_generated_metadata: Metadata extracted or enhanced by AI.
  ai_generated_metadata_with_celebrity: AI-generated metadata
    focusing on celebrities mentioned in the video (default: None).
  """

  def __init__(
      self,
      video_id: str,
      uri: str | None,
      title: str | None = None,
      description: str | None = None,
      metadata: str | None = None,
      transcript: str | None = None,
      summary: str | None = None,
      languages: str | None = None,
      duration: str | None = None,
      ai_generated_metadata: str | None = None,
      ai_suggested_titles: str | None = None,
      ai_generated_metadata_with_celebrity: str | None = None,
      ai_suggested_external_summary: str | None = None,
  ):
    # From MRSS
    self.video_id = video_id
    self.title = title
    self.description = description
    self.uri = uri
    self.duration = duration
    self.metadata = metadata if metadata else {}
    # AI Generated
    self.languages = languages
    self.transcript = transcript
    self.summary = summary
    self.ai_suggested_titles = ai_suggested_titles
    self.ai_suggested_external_summary = ai_suggested_external_summary
    # Metadata
    self.ai_generated_metadata = ai_generated_metadata
    self.ai_generated_metadata_with_celebrity = (
        ai_generated_metadata_with_celebrity
    )

  def detect_duration(self) -> float:
    """Returns the duration of the video.

    If duration is unknown, ffmpeg will be used to calculate the value.

    Returns:
      The duration of the video in seconds. Returns -1.0 if there
        is an error.
    """
    if self.duration:
      return self.duration
    # Command to get video duration using ffprobe, which is part of the ffmpeg suite
    command = (
        "ffprobe -v error -show_entries format=duration -of"
        f" default=noprint_wrappers=1:nokey=1 {shlex.quote(self.uri)}"
    )
    try:
      # Execute the command
      result = subprocess.run(
          shlex.split(command),
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE,
          text=True,
      )
      # Check if the command was successful
      if result.returncode == 0:
        # Return the duration as a float
        self.duration = result
        return float(result.stdout.strip())
      else:
        print(f"Error fetching video duration: {result.stderr}")
    except Exception as e:
      print(f"Failed to run command: {e}")

    return -1.0
