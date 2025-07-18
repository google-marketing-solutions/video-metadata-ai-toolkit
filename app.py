"""Flask application for AI metadata generation.

This module provides a REST API to interact with AI models for tasks such as
content title suggestion, summarization, tagging, IAB categorization, and
description.
"""

import functools
import os
from typing import Callable
from ai_metadata import ai_metadata_generator
from ai_metadata import file_io
from ai_metadata import models
import flask
from google.cloud import videointelligence
from smart_ad_breaks import cue_point_generator
from smart_ad_breaks import video_analysis
from werkzeug import exceptions
from werkzeug import Response

app = flask.Flask(__name__)

# Use Vertex AI by default
llm = models.create_gemini_llm_with_vertex()


def get_gcs_path(f: Callable[..., Response]) -> Callable[..., Response]:
  """A decorator that extracts a GCS path from a JSON request body.

  This decorator expects a JSON object with a 'gcs_path' key.
  If the 'gcs_path' is not provided, it returns a 400 error.

  Args:
    f: The function to be decorated. This function should accept `content_path`
      (a string representing a GCS path) as its first argument, followed by any
      other arguments (`*args`, `**kwargs`) it normally expects.

  Returns:
    A decorated function that extracts the 'gcs_path' from the incoming Flask
    request and passes it as the first argument to the original function.
  """

  @functools.wraps(f)
  def decorated_function(*args, **kwargs) -> Response:
    if not flask.request.is_json or 'gcs_path' not in flask.request.json:
      return (
          flask.jsonify({'error': 'Request must be JSON with a gcs_path key'}),
          400,
      )
    content_path = flask.request.json['gcs_path']

    try:
      return f(content_path, *args, **kwargs)
    except KeyError as e:
      return flask.jsonify({'error': f'Missing key in JSON: {str(e)}'}), 400
    except (ValueError, TypeError) as e:
      app.logger.exception('Error processing request:')
      return flask.jsonify({'error': str(e)}), 500

  return decorated_function


@app.route('/title', methods=['POST'])
@get_gcs_path
def title(content_path: str) -> Response:
  """Suggests titles for the content at the given GCS path.

  Args:
    content_path: The GCS path to the content file.

  Returns:
    A JSON response containing a list of suggested titles.
  """
  result = ai_metadata_generator.suggest_titles(
      file_io.File(content_path), language_model=llm
  )
  return flask.jsonify(result)


@app.route('/summarize', methods=['POST'])
@get_gcs_path
def summarize(content_path: str) -> Response:
  """Summarizes the content at the given GCS path.

  Args:
    content_path: The GCS path to the content file.

  Returns:
    A JSON response containing the summary of the content.
  """
  result = ai_metadata_generator.summarize(
      file_io.File(content_path), language_model=llm
  )
  return flask.jsonify(result)


@app.route('/tag', methods=['POST'])
@get_gcs_path
def tag(content_path: str) -> Response:
  """Generates metadata tags for the content at the given GCS path.

  This endpoint can either generate free-form tags or key-value pairs
  based on the provided keys in the request body.

  Args:
    content_path: The GCS path to the content file.

  Returns:
    A JSON response containing a list of tags or a dictionary of key-value
    pairs.
  """
  keys = flask.request.json.get('keys', [])
  if keys:
    result = ai_metadata_generator.generate_key_values(
        file_io.File(content_path), keys, language_model=llm
    )
  else:
    result = ai_metadata_generator.generate_metadata(
        file_io.File(content_path), language_model=llm
    )
  return flask.jsonify(result)


@app.route('/iab', methods=['POST'])
@get_gcs_path
def iab(content_path: str) -> Response:
  """Generates IAB categories for the content at the given GCS path.

  Args:
    content_path: The GCS path to the content file.

  Returns:
    A JSON response containing a list of IAB categories.
  """
  result = ai_metadata_generator.generate_iab_categories(
      file_io.File(content_path), language_model=llm
  )
  return flask.jsonify(result)


@app.route('/describe', methods=['POST'])
@get_gcs_path
def describe(content_path: str) -> Response:
  """Describes the content at the given GCS path.

  Args:
    content_path: The GCS path to the content file.

  Returns:
    A JSON response containing the description of the content.
  """
  result = ai_metadata_generator.describe(
      file_io.File(content_path), language_model=llm
  )
  return flask.jsonify(result)


@app.route('/cues', methods=['POST'])
@get_gcs_path
def cues(content_path: str):
  """Generates cue points for the content at the given GCS path.

  Args:
    content_path: The GCS path to the content file.

  Returns:
    A JSON response containing a list of cue points.
  """
  video_intel_client = videointelligence.VideoIntelligenceServiceClient()
  video_analyzer = video_analysis.CloudVideoAnalyzer(video_intel_client)
  minimum_time_for_first_cue_point = flask.request.json.get(
      'minimum_time_for_first_cue_point', 0.0
  )
  minimum_time_between_cue_points = flask.request.json.get(
      'minimum_time_between_cue_points', 30
  )
  cue_points = cue_point_generator.determine_video_cue_points(
      content_path,
      video_analyzer,
      minimum_time_for_first_cue_point=minimum_time_for_first_cue_point,
      minimum_time_between_cue_points=minimum_time_between_cue_points,
  )
  return flask.jsonify(cue_points)


@app.route('/', methods=['GET'])
def health_check() -> Response:
  """Returns a 200 OK status for health checks.

  Returns:
    A string "OK" with a 200 status code.
  """
  return 'OK'


@app.errorhandler(exceptions.InternalServerError)
def handle_500(e):
  """Handles 500 errors, providing a user-friendly JSON response."""
  original = getattr(e, 'original_exception', None)
  if original:
    app.logger.exception(
        'An unhandled exception occurred during request processing:'
    )
  else:
    app.logger.error('An internal server error occurred.', exc_info=e)

  response_payload = {'error': 'An internal server error occurred.'}
  return flask.jsonify(response_payload), 500


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
