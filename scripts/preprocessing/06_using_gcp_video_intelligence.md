# Process

We used Cloud Functions and Cloud Buckets in Google Cloud Platform to read text from our videos with Google's Video Intelligence API. We wrote a cloud function that triggers the API when objects are uploaded to an input bucket and writes the output to another bucket. We then pull the JSON files from the bucket into our local environment for analysis. 


"""This is the Cloud Function"""
"""Detect text in a video stored on GCS."""
import time

from google.cloud import videointelligence

OUTPUT_BUCKET="gs://moj-text-detection-output"

video_client = videointelligence.VideoIntelligenceServiceClient()
features = [videointelligence.Feature.TEXT_DETECTION]

def detect_text(event, context):
  print(event)
  input_uri = "gs://" + event["bucket"] + "/" + event["name"]
  file_stem = event["name"].split(".")[0]
  output_uri = f"{OUTPUT_BUCKET}/{file_stem} - {time.time()}.json"

  video_client.annotate_video(
      request={
        "features": features, 
        "input_uri": input_uri, 
        "output_uri": output_uri
        }
  )

  print("Processing video for text detection. ", input_uri)
