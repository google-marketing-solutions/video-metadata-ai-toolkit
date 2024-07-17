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
from unittest.mock import patch, mock_open, MagicMock
from video_class import Video
import transcription_utils
import ai_metadata_generator

class TestVideoMetadataGenerator(unittest.TestCase):

    def test_get_video_id_from_url(self):
        """Tests getting video id from a valid and invalid URL."""
        url = "https://bcboltbde696aa-a.akamaihd.net/media/v1/pmp4/static/clear/6286608028001/1234abcd/main.mp4"
        expected_id = "1234abcd"
        self.assertEqual(ai_metadata_generator._get_video_id_from_url(url), expected_id)

        url_no_match = "https://example.com/video/1234abcd"
        self.assertIsNone(ai_metadata_generator._get_video_id_from_url(url_no_match))

    @patch('transcription_utils.download_video')
    @patch('transcription_utils.extract_audio_from_video')
    @patch('transcription_utils.upload_local_file_to_google_cloud')
    @patch('transcription_utils.transcribe_audio')
    @patch('builtins.open', new_callable=mock_open, read_data="This is a transcript.")
    @patch('os.path.exists')
    def test_get_transcription_from_video(
        self,
        mock_exists,
        mock_open,
        mock_transcribe_audio,
        mock_upload_local_file_to_google_cloud,
        mock_extract_audio_from_video,
        mock_download_video
    ):
        """Tests succesfully getting a trancript from a video."""
        video = Video(id="1234", uri="https://example.com/video.mp4")
        audio_bucket_name = "audio_bucket"
        transcript_bucket_name = "transcript_bucket"

        mock_exists.return_value = False
        mock_download_video.return_value = "./vids/1234_tmp_vid.mp4"
        mock_extract_audio_from_video.return_value = "./audios/1234.wav"
        mock_upload_local_file_to_google_cloud.return_value = "gs://audio_bucket/1234.wav"
        mock_transcribe_audio.return_value = "./transcriptions/1234_transcription.txt"

        transcript = ai_metadata_generator._get_transcription_from_video(video, audio_bucket_name, transcript_bucket_name)
        self.assertEqual(transcript, "This is a transcript.")

        # Test when the local video file already exists
        mock_exists.side_effect = [True]
        transcript = ai_metadata_generator._get_transcription_from_video(video, audio_bucket_name, transcript_bucket_name)
        self.assertEqual(transcript, "This is a transcript.")


    @patch('ai_metadata_generator._get_transcription_from_video', return_value="This is a long transcript with more than 100 characters. This ensures the transcription length condition is satisfied.")
    @patch('llm_utils.call_llm')
    def test_add_ai_attributes_to_video(self, mock_call_llm, mock_get_transcription_from_video):
        """Tests adding ai attributes to a video (e.g. metadata/summary/titles)."""
        video = Video(id="1234", uri="https://example.com/video.mp4")
        video.duration = 1200
        audio_bucket_name = "audio_bucket"
        transcript_bucket_name = "transcript_bucket"

        mock_call_llm.side_effect = [
            "Generated summary",
            "Generated metadata",
            ["Title 1", "Title 2"],
            "Generated external summary"
        ]

        ai_metadata_generator._add_ai_attributes_to_video(video, audio_bucket_name, transcript_bucket_name)

        self.assertEqual(video.transcript, "This is a long transcript with more than 100 characters. This ensures the transcription length condition is satisfied.")
        self.assertEqual(video.summary, "Generated summary")
        self.assertEqual(video.ai_generated_metadata, "Generated metadata")
        self.assertEqual(video.ai_suggested_titles, ["Title 1", "Title 2"])
        self.assertEqual(video.ai_suggested_external_summary, "Generated external summary")

    @patch('ai_metadata_generator._get_transcription_from_video', return_value="Short transcript")
    @patch('llm_utils.call_llm')
    def test_add_ai_attributes_to_video_short_transcript(self, mock_call_llm, mock_get_transcription_from_video):
        """Tests for when the transcript is too short and no genAI should be pursued."""
        video = Video(id="1234", uri="https://example.com/video.mp4")
        video.duration = 1200
        audio_bucket_name = "audio_bucket"
        transcript_bucket_name = "transcript_bucket"

        ai_metadata_generator._add_ai_attributes_to_video(video, audio_bucket_name, transcript_bucket_name)

        self.assertEqual(video.transcript, "Short transcript")
        self.assertIsNone(video.summary)
        self.assertIsNone(video.ai_generated_metadata)
        self.assertIsNone(video.ai_suggested_titles)
        self.assertIsNone(video.ai_suggested_external_summary)
        mock_call_llm.assert_not_called()


    @patch('ai_metadata_generator._get_transcription_from_video', return_value="This is a video longer than 40 minutes.")
    @patch('llm_utils.call_llm')
    def test_add_ai_attributes_to_video_longer_than_40_minutes(self, mock_call_llm, mock_get_transcription_from_video):
        """Tests for when the video is too long and should not have ai attributes added."""
        video = Video(id="1234", uri="https://example.com/video.mp4")
        video.duration = 3400
        audio_bucket_name = "audio_bucket"
        transcript_bucket_name = "transcript_bucket"

        ai_metadata_generator._add_ai_attributes_to_video(video, audio_bucket_name, transcript_bucket_name)

        self.assertEqual(video.transcript, "This is a video longer than 40 minutes.")
        self.assertIsNone(video.summary)
        self.assertIsNone(video.ai_generated_metadata)
        self.assertIsNone(video.ai_suggested_titles)
        self.assertIsNone(video.ai_suggested_external_summary)
        mock_call_llm.assert_not_called()



    @patch('ai_metadata_generator._add_ai_attributes_to_video')
    @patch('ai_metadata_generator._get_video_id_from_url', return_value="1234abcd")
    def test_main(self, mock_get_video_id_from_url, mock_add_ai_attributes_to_video):
        """Tests the main function which takes in a video and adds ai attributes."""
        video_url = "https://bcboltbde696aa-a.akamaihd.net/media/v1/pmp4/static/clear/6286608028001/1234abcd/main.mp4"
        metadata = "test metadata"
        video_title = "test title"
        audio_bucket_name = "audio_bucket"
        transcript_bucket_name = "transcript_bucket"

        result_video = ai_metadata_generator.main(
            video_id=None,
            video_url=video_url,
            metadata=metadata,
            video_title=video_title,
            audio_bucket_name=audio_bucket_name,
            transcript_bucket_name=transcript_bucket_name
        )

        self.assertEqual(result_video.id, "1234abcd")
        self.assertEqual(result_video.uri, video_url)
        self.assertEqual(result_video.metadata, metadata)
        self.assertEqual(result_video.title, video_title)
        mock_add_ai_attributes_to_video.assert_called_once_with(result_video, audio_bucket_name, transcript_bucket_name)


    def test_main_no_video_url(self):
        """Tests the main function throws error when no video URL is provided."""
        with self.assertRaises(ValueError):
            ai_metadata_generator.main(
                video_id="1234",
                video_url="",
                metadata="test metadata",
                video_title="test title",
                audio_bucket_name="audio_bucket",
                transcript_bucket_name="transcript_bucket"
            )

if __name__ == '__main__':
    unittest.main()
