## **Metadata AI Toolkit**

### **Disclaimer**

This is not an officially supported Google product. The code samples shared here
are not formally supported by Google and are provided only as a reference.

### **Introduction**

This repository currently houses four different video metadata related
solutions:
- AI Metadata: Use LLMs to generate metadata and descriptions for text, images, and video content.
- Smart Ad Breaks: Identify suitable cue points for VOD content based on shot
changes.
- Celebrity Detection: Identify celebrities in video content using GCP's
celebrity detection API (soon to be deprecated.)
- Image Metadata: Identify things/objects in video content.

### Colab

Try AI Metadata in Colab!

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-marketing-solutions/video-metadata-ai-toolkit/blob/main/ai_metadata/colab/ai_metadata.ipynb)

### Setup

1.  Create a Python virual environment.

2.  From inside the environment run `pip install -r requirements.txt`.

3.  Setup Google Cloud:

Most of the features of this project are available with just a Gemini API key:

```bash
export GEMINI_API_KEY='YOUR_API_KEY'
```

If you would like to analyze content hosted on Google Cloud Storage ("gs://.."), you will also need to [enable the Vertex API](https://cloud.google.com/endpoints/docs/openapi/enable-api) in your cloud project and configure your Google Cloud Application Default Credentials:

```bash
gcloud auth application-default login
```

For cue point generation, make sure you have FFMPEG installed, or if you want to generate cue points for files hosted on GCP you will also need to activate the Video Intelligence API and setup your ADC.

### Command Line Interface


```
usage: generate_metadata.py [-h] [--keys KEYS [KEYS ...]] [--first_cue FIRST_CUE] [--between_cues BETWEEN_CUES]
               [--volume_threshold VOLUME_THRESHOLD]
               {describe,summarize,tag,title,iab,cues} content_file

Analyzes content using AI.

positional arguments:
  {describe,summarize,tag,title,iab,cues}
                        The action to perform for the provided content. Valid actions are:
                          title: suggests possible titles for the content
                          describe: describes the content with as much detail as possible
                          summarize: summarizes the content for an external audience
                          tag: identifies keywords related to the content (use with --keys to specify custom keys)
                          iab: identifies IAB content and audience categories related to the content
                          cues: identifies suitable ad cue point placement for video content
  content_file          The URI of the content to be processed. Files hosted on GCS should use the prefix gs:// and require Application Default Credentials with a default project to be configured.

options:
  -h, --help            show this help message and exit
  --keys KEYS [KEYS ...]
                        Use with "tag" to create key/values instead of free-form metadata values. No-op otherwise.
  --first_cue FIRST_CUE, -f FIRST_CUE
                        Use with "cues" to specify the earliest time that a cue point shouldbe created. Defaults to "0.0."
  --between_cues BETWEEN_CUES, -b BETWEEN_CUES
                        Use with "cues" to specify the minimum amount of time that should be between two cue points. Defaults to 30.0.
  --volume_threshold VOLUME_THRESHOLD, -v VOLUME_THRESHOLD
                        Use with "cues." If provided, the maximum in volume, in dB, for a cue point. This is always a no-op for files hosted on GCP.
```

For example, to generate tags for a video (the keys are optional):

```bash
python generate_metadata.py tag my/video/uri.mp4 --keys key1 key2 key3
```


### **Deployment**

To deploy the AI Metadata Generator as a Cloud Run service, follow these steps:

1.  **Create Artifact Registry Repository:**
```bash
gcloud artifacts repositories create YOUR_ARTIFACT_REGISTRY_REPO_NAME \
--repository-format=docker \
--location=YOUR_GCP_REGION \
--description="Docker repository for Video Metadata project" \
--project=YOUR_PROJECT_ID
```

2.  **Push the image to Cloud Build:**
```bash
gcloud builds submit --tag [YOUR_REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[YOUR_ARTIFACT_REGISTRY_REPO_NAME]/[YOUR_IMAGE_NAME]:v1.0 .
```

3.  **Deploy the service to Cloud Run:**
```bash
gcloud run deploy content-metadata-service \
--image [YOUR_REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[YOUR_ARTIFACT_REGISTRY_REPO_NAME]/[YOUR_IMAGE_NAME]:v1.0 \
--region [YOUR_REGION]
```

4.  **Test the service:**

If the service has been deployed successfully, you should now have a service endpoint. You can hit that endpoint to test the service (authenticaion required):

Health Check (will return OK if the service is working):

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)"  [YOUR_ENDPOINT_URL]
```

Tagging content hosted on GCS:

```bash
curl -X POST \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $(gcloud auth print-identity-token)" \
-d '{"gcs_path":"gs://path/to/your/content"}' \
[YOUR_ENDPOINT_URL]/tag
```

### **Scripts**

To manually run tests and the linter:

```
sh test_and_lint.sh
```
### **Upgrading Dependencies**

pip-compile is used to generate the ```requirements.txt``` file. To update
dependencies, make changes to ```requirements.in``` and then use the following
command:

```
pip-compile requirements.in --generate-hashes --upgrade -o requirements.txt
```
