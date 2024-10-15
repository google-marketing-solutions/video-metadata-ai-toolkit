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

"""Entry point for Video AI Metadata Generator project."""

import logging
import os
import re
from typing import Any, Optional

import llm_utils
import project_configs
import transcription_utils
from video_class import Video


def _get_video_id_from_url(video_url: str) -> Optional[str]:
  """Extracts and returns a video ID from a URL based on a predefined pattern.

  This function specifically checks if the URL contains 'bcboltbde696aa' to
  determine if it should proceed with extraction. If the URL matches this
  criterion, the function uses a regex pattern to find and return a UUID-like
  segment which represents the video ID. This segment is expected to be in a
  specific format and position within the URL path.

  Note:
   The URL pattern is expected to be like:
    'https://bcboltbde696aa-a.akamaihd.net/media/v1/pmp4/static/clear/<numeric-segment>/<UUID-like-segment>/...'
    where '<numeric-segment>' is a placeholder for any numeric value and
    '<UUID-like-segment>' is the expected video ID to be extracted.

  Args:
    video_url (str): The URL from which the video ID should be extracted.

  Returns:
    str or None: The extracted video ID if found, otherwise None if the URL does
    not contain 'bcboltbde696aa' or if no ID is found following the expected
    pattern.
  """
  if "bcboltbde696aa" in video_url:
    # Only works for the videos which start like this URL:
    pattern = r"https://bcboltbde696aa-a.akamaihd.net/media/v1/pmp4/static/clear/\d+/([^/]+)"
    match = re.search(pattern, video_url)
    if match:
      return match.group(1)  # Returns the captured UUID-like segment
  return None


def _get_transcription_from_video(
    video: Video, audio_bucket_name: str, transcript_bucket_name: str
) -> Optional[str]:
  """Gets a transcript from a video.

  Args:
    video (Video): The Video object to get the transcription for.
    audio_bucket_name (str): Name of the audio bucket in Google Cloud Storage.
    transcript_bucket_name (str): Name of the transcript bucket in Google Cloud
      Storage.

  Returns:
    The text of the transcript, or None if the transcription fails.
  """
  video_uri = video.uri
  video_id = video.id
  languages = video.languages
  local_video_file_path = os.path.join("./vids/", video_id + "_tmp_vid.mp4")

  if video_uri.startswith("https://") or video_uri.startswith("gs://"):
    if not os.path.exists(local_video_file_path):
      try:
        # 1. Download video locally
        local_video_file_path = transcription_utils.download_video(
            video_uri, local_video_file_path
        )
      except Exception as e:
        logging.error(f"Failed to process video {video_id}: {e}")
        return None
    else:
      # Video is already downloaded.
      local_transcript_filename = os.path.join(
          "./transcriptions/", video_id + "_transcription.txt"
      )
      with open(local_transcript_filename, "r") as file:
        transcript = file.read()
      return transcript

  # Else it is a local file.
  else:
    local_video_file_path = video_uri
  # 2. Strip the audio using ffmpeg
  local_audio_file_path = transcription_utils.extract_audio_from_video(
      local_video_file_path, "./audios"
  )
  # 3. Upload the audio file to GCP
  audio_file_cloud_uri = transcription_utils.upload_local_file_to_google_cloud(
      audio_bucket_name, local_audio_file_path, f"{video_id}.wav"
  )
  # 4. Create the transcript
  local_transcript_filename = transcription_utils.transcribe_audio(
      audio_file_cloud_uri, languages
  )
  with open(local_transcript_filename, "r") as file:
    transcript = file.read()
  print(transcript)
  return transcript


def _add_ai_attributes_to_video(
    video: Video, audio_bucket_name: str, transcript_bucket_name: str
) -> None:
  """Enhances a Video object with AI-generated attributes.

  This function performs the following steps:
  1. Retrieves the transcript of the video and assigns it to the video object.
  2. Checks if the transcript length is sufficient and the video duration is
    below a threshold.
  3. Generates and assigns a summary of the video using an AI model.
  4. Generates and assigns AI-generated metadata for the video.
  5. Generates and assigns AI-suggested titles for the video.
  6. Generates and assigns an AI-suggested external summary for the video.

  Args:
    video (Video): The Video object to be enhanced with AI-generated attributes.
    audio_bucket_name (str): The name of the audio bucket in Google Cloud
      Storage.
    transcript_bucket_name (str): The name of the transcript bucket in Google
      Cloud Storage.

  Returns:
    None

  Raises:
    IOError: If there is an issue with retrieving or processing the transcript.
  """
  video.transcript = _get_transcription_from_video(
      video,
      audio_bucket_name,
      transcript_bucket_name,
  )
  # If the transcript is not long enough (<100 characters), or
  # the video is too long (> 40 minutes), do not proceed with genAI.
  if len(video.transcript) > 100 and video.duration < 2400:
    video.summary = llm_utils.call_llm(video, "generate_summary")
    video.ai_generated_metadata = llm_utils.call_llm(video, "generate_metadata")
    print("ai_generated_metadata=", video.ai_generated_metadata)
    video.ai_suggested_titles = llm_utils.call_llm(
        video, "generate_title_options"
    )
    video.ai_suggested_external_summary = llm_utils.call_llm(
        video, "generate_external_summary"
    )


def main(
    video_id,
    video_url,
    metadata="",
    video_title="",
    audio_bucket_name=project_configs.AUDIO_BUCKET_NAME,
    transcript_bucket_name=project_configs.TRANSCRIPT_BUCKET_NAME,
) -> Video:
  """Main function to process a video and generate AI attributes.

  This function processes a video by generating its AI attributes, such as
  transcript, summary, metadata, title suggestions, and external summary. It
  takes video details as input, processes the video, and returns a Video object
  with the generated attributes.

  Args:
    video_id (str): The unique identifier of the video. If not provided, it will
      be extracted from the video URL.
    video_url (str): The URL of the video to be processed.
    metadata (str, optional): Metadata associated with the video. Defaults to an
      empty string.
    video_title (str, optional): The title of the video. Defaults to an empty
      string.
    audio_bucket_name (str, optional): The name of the audio bucket in Google
      Cloud Storage. Defaults to project_configs.AUDIO_BUCKET_NAME.
    transcript_bucket_name (str, optional): The name of the transcript bucket in
      Google Cloud Storage. Defaults to project_configs.TRANSCRIPT_BUCKET_NAME.

  Returns:
    Video: The processed Video object with generated AI attributes.

  Raises:
    ValueError: If no video URL is specified.
  """
  if not video_url:
    raise ValueError("No video URL specified.")

  video_id = video_id or _get_video_id_from_url(video_url)
  video = Video(video_id, uri=video_url, metadata=metadata, title=video_title)
  _add_ai_attributes_to_video(video, audio_bucket_name, transcript_bucket_name)
  return video


if __name__ == "__main__":
  main()
