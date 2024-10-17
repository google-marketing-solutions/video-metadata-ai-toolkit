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
import ast
from typing import Any
import project_configs
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from video_class import Video

# Constants for the file
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: (
        generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: (
        generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: (
        generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: (
        generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
}

# Define the different prompts according to which attribute of the video the
# prompt is trying to generate.
PROMPTS = {
    "generate_metadata": (
        """You are given a title of a video, the transcript of the 
           video, and a summary of the video. Please generate as much metadata as possible. 
           DO NOT USE MARKDOWN. Do not give a description, just provide metadata tags of 
           the video. For example, quiz,
                        premier league,
                        la liga,
                        robert lewandowski,
                        football,
                        zlatan ibrahimovic,
                        goal,
                        goal.com,
                        netherlands,
                        mario balotelli,
                        soccer,
                        bundesliga,
                        serie a,
                        striker,
                        inter milan,
                        football heads up,
                        games,
                        youtube,
                        david kufi,
                        subscribe,
                        yani,
                        ali,
                        yarns,
    Please order the tags in order of significance (most to least)
    Title: {title}
    Transcript: {transcript}
    Summary: {summary}"""
    ),
    "generate_summary": """Summarize this video transcript. Make it no longer than a 5 sentence summary. If it is in another language, output your summary in English. Transcript: {title} {transcript}""",
    "generate_title_options": (
        """Generate a punchy, catchy, and viral title for a video. 
                                 The title should capture the essence of the video and entice viewers to 
                                 click and watch. Use the provided summary and transcript to understand the 
                                 key points and highlights of the video. Only output the titles, nothing else. 
                                 Put each title in quotes and put them all in a list, for example like 
                                 this: ["Football Fan Face-Off: Messi vs. Ronaldo, VAR Drama & Will Spurs 
                                 EVER Win?", "Football's Most CONTROVERSIAL Opinions: This Debate Will Make 
                                 You MAD (Or Agree!)", ...] DO NOT USE MARKDOWN. Do not use python.
                                 Summary: {summary}
                                 Transcript: {transcript}
                                 Title:"""
    ),
    "generate_external_summary": (
        """Generate an engaging and enticing summary for a video
                                    that will captivate viewers and make them eager to watch it. Use the provided
                                    summary, title options, and transcript to understand the key points and
                                    highlights of the video. The summary should be appealing, informative, and
                                    encourage viewers to click on the video. For example, "Bayern Munich star Harry Kane takes on Front Three content creator Yarns in a selection of tricky quiz challenges - who will win?"
                                    Video Summary: {summary}  
                                    Title Options:
                                    {title_options} 
                                    Transcript Excerpt:
                                    {transcript_excerpt}  
                                    User-Facing Summary:"""
    ),
}


def _get_prompt(video: Video, attribute_to_generate: str) -> str:
  """Generates the appropriate prompt based on the attribute to generate.

  Args:
      video (Video): The Video object containing the necessary data.
      attribute_to_generate (str): The type of attribute to generate (e.g.,
        "generate_metadata", "generate_summary", "generate_title_options",
        "generate_external_summary").

  Returns:
      str: The formatted prompt string to be used by the LLM.

  Raises:
      ValueError: If the attribute_to_generate is not recognized or supported.
  """
  if attribute_to_generate not in PROMPTS:
    raise ValueError(f"Unknown attribute to generate: {attribute_to_generate}")

  prompt_template = PROMPTS[attribute_to_generate]

  if attribute_to_generate == "generate_metadata":
    prompt = prompt_template.format(
        title=video.title, transcript=video.transcript, summary=video.summary
    )
  elif attribute_to_generate == "generate_summary":
    prompt = prompt_template.format(
        title=video.title, transcript=video.transcript
    )
  elif attribute_to_generate == "generate_title_options":
    prompt = prompt_template.format(
        summary=video.summary, transcript=video.transcript
    )
  elif attribute_to_generate == "generate_external_summary":
    title_options_str = "\n".join(
        [f"{i+1}. {title}" for i, title in enumerate(video.ai_suggested_titles)]
    )
    transcript_excerpt = video.transcript[:500]  # Adjust length as needed
    prompt = prompt_template.format(
        summary=video.summary,
        title_options=title_options_str,
        transcript_excerpt=transcript_excerpt,
    )
  else:
    raise ValueError(
        f"Unsupported attribute to generate: {attribute_to_generate}"
    )
  return prompt


def call_llm(video: Video, attribute_to_generate: str) -> Any:
  """Calls the LLM with the appropriate prompt.

  Args:
    video (Video): The Video object to generate the attribute for.
    attribute_to_generate (str): The type of attribute to generate (e.g.,
      "generate_metadata", "generate_summary", "generate_title_options",
      "generate_external_summary").

  Returns:
    Any: The LLM generated attribute. The exact type of return value depends
      on the attribute to generate. For example, a string for summaries or a
      list of strings for title options.

  Raises:
    ValueError: If the attribute_to_generate is not recognized or supported.
  """
  vertexai.init(project=project_configs.PROJECT_ID, location="us-central1")
  model = GenerativeModel("gemini-1.5-pro-preview-0409")
  prompt = _get_prompt(video, attribute_to_generate)
  try:
    response = model.generate_content(
        [prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )
    if attribute_to_generate == "generate_title_options":
      if response.text.startswith("```python") and response.text.endswith(
          "```"
      ):
        # Strip out the backticks from the LLM's markdown response.
        response.text = response.text[9:-3].strip()
      try:
        titles = ast.literal_eval(response.text)
        if isinstance(titles, list) and all(
            isinstance(title, str) for title in titles
        ):
          return titles
      except (SyntaxError, ValueError):
        print("Failed to parse the LLM response into a list of titles.")
        return response.text
    return response.text.strip()
  except Exception as e:
    print(
        f"Failed to generate {attribute_to_generate} for video"
        f" {video.video_id}: {e}"
    )
    return ""
