## Video Metadata Toolkit

### Disclaimer

This is not an officially supported Google product. The code samples shared here

are not formally supported by Google and are provided only as a reference.

### Introduction

This repo currently houses two different use cases: AI Tags (generate metadata
for your videos using AI) and Smart Ad Breaks (generate cue points for your VOD
and live video content to insert ads at the right moments).

### AI Tags Development

#### Setup

1.  Create a Python virual environment.

2.  From inside the environment run `pip install -r requirements.txt`.

3.  If you plan to run anything locally, setup your Application Default
    Credentials and project ID for GCP.

4.  Make sure to run the code from within the video_metadata_toolkit directory.

Application Default Credentials:

```

gcloud auth application-default login

```

Set project ID:

```

gcloud config set project [PROJECT_ID]

```

Input your GCP project ID into the project_configs.py file.

#### Google Cloud

You need a Google Cloud Project to each of these use cases.

These are the APIs you need to enable for the AI-generated metadata tags.

*   Cloud Storage

*   Cloud Translation API

*   Cloud Storage

*   Cloud Storage API

*   Cloud Speech-to-Text API

*   Vertex AI API

##### Run AI Tags Code

[ai_metadata_generator.py](https://github.com/google-marketing-solutions/video-metadata-ai-toolkit/video-metadata-ai-toolkit/ai_metadata_generator.py) has the function which is the main entry point for
running the code:

```

main(

video_id,

video_url,

metadata="",

video_title="",

audio_bucket_name=project_configs.AUDIO_BUCKET_NAME,

transcript_bucket_name=project_configs.TRANSCRIPT_BUCKET_NAME,

)

```

#### Run tests

From the top level project directory:

```

python -m unittest discover video_metadata_toolkit -p "*_test.py"

```

## Code format

Submitted code should conform to Google's Python style guide. To format code
automatically, run `pyink --pyink-indentation=2 -l 80 [FILENAME]`.

For VS Code users, you can configure the formatter to run automatically by
adding the following to your `settings.json`:

```

"[python]": {

"editor.defaultFormatter": "ms-python.black-formatter",

"editor.formatOnSave": true,

"editor.formatOnPaste": true,

"editor.formatOnType": true

},

"black-formatter.args": [

"--pyink-indentation=2"

],

"black-formatter.path": [

"pyink"

],

```

#### Scripts

To manually run tests and the linter:

```

sh test_and_lint.sh

```
