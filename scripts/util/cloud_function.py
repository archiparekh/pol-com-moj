import os
from moviepy.editor import *
from datetime import datetime

base_path = "audio"

video_files = os.listdir(base_path)

starttime = datetime.now()
for i, file in enumerate(video_files):
  try:
    video = VideoFileClip(f"{base_path}/{file}")

    audio_path = f"{base_path}/{file[:-1]}3"
    video.audio.write_audiofile(audio_path)
  except:
    print(f"FAIL: {file}")

endtime = datetime.now()
print(endtime - starttime)

# --- remaining files
import os
import whisper
import json
from datetime import datetime

model = whisper.load_model("small")
starttime = datetime.now()
base_path = "audio"

files = os.listdir(f"{base_path}")
for i,file in enumerate(files):
  result = model.transcribe(f"{base_path}/{file}")
  output = json.dumps({
      "file": file,
      "text": result["text"], 
      "lang": result["language"]
  }, indent=4)
  with open(f"output/{file[:-4]}.json", "w") as outfile:
      outfile.write(output)
  if (i%20 == 0):
    print(f"TIME ELAPSED for {i}: ", datetime.now() - starttime)
# ---

import os
import whisper
import json
from datetime import datetime

model = whisper.load_model("small")
starttime = datetime.now()
base_path = "audio"
folders = os.listdir(base_path)
for folder in folders: 
  files = os.listdir(f"{base_path}/{folder}")
  for i,file in enumerate(files):
    result = model.transcribe(f"{base_path}/{folder}/{file}")
    output = json.dumps({
        "file": file,
        "text": result["text"], 
        "lang": result["language"]
    }, indent=4)
    with open(f"output/{folder}/{file[:-4]}.json", "w") as outfile:
        outfile.write(output)
    if (i%20 == 0):
      print(f"TIME ELAPSED for {i}: ", datetime.now() - starttime)


# For testing
import os
import whisper
import json
from datetime import datetime

model = whisper.load_model("small")
starttime = datetime.now()
base_path = "group"
folders = os.listdir(base_path)
for folder in folders: 
  files = os.listdir(f"{base_path}/{folder}")
  for i,file in enumerate(files[:2]):
    result = model.transcribe(f"{base_path}/{folder}/{file}")
    output = json.dumps({
        "file": file,
        "text": result["text"], 
        "lang": result["language"]
    }, indent=4)
    with open(f"test_output/{folder}/{file[:-4]}.json", "w") as outfile:
        outfile.write(output)
    if (i%2 == 0):
      print(f"TIME ELAPSED for {i}: ", datetime.now() - starttime)

"""
The Process is as follows:
sudo apt install python3-pip
sudo apt-get install ffmpeg
cd myproj
  source env/bin/activate 

mkdir group
cd group
mkdir videos_2
cd videos_2
gcloud storage cp gs://input-moj-audios/group1/videos_4/videos_4/*.mp3 .
gcloud storage cp gs://input-moj-audios/group2/videos_5/videos_5/*.mp3 .
gcloud storage cp gs://input-moj-audios/group4/videos_16/videos_16/*.mp3 videos_16
gcloud storage cp gs://input-moj-audios/videos_18/videos_18/*.mp3 videos_18


gcloud storage cp gs://input-audio-3435/output/*.mp3 .

gcloud storage cp gs://input-moj-videos/videos_1/videos_1/*.mp4 .


-- for new one
gcloud compute scp ../Downloads/remaining_audio/remaining_audio/.*mp3 instance-20240324-180322:myproj/audio


--

nohup python3 -u speech.py 

gcloud storage cp --recursive myproj/output/  gs://input-audio-3435

 gcloud storage cp --recursive myproj/output/videos_2  gs://output-moj-audio
  gcloud storage cp --recursive myproj/output/videos_3  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_4  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_1  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_5  gs://output-moj-audio &
   gcloud storage cp --recursive myproj/output/videos_6  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_7  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_8  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_9  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_10  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_11  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_12  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_13  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_14  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_15  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_16  gs://output-moj-audio
   gcloud storage cp --recursive myproj/output/videos_18  gs://output-moj-audio
   

"""



    gcloud storage cp --recursive myproj/videos_17  gs://output-moj-audio/videos_17

gcloud storage cp my-proj/videos_17/doeN733ZoNtXepVOb3LLfVNPD5JGPmSQ6Zmb.json gs://output-moj-audio
gcloud storage cp gs://input-moj-audios  my-proj/videos_17/doeN733ZoNtXepVOb3LLfVNPD5JGPmSQ6Zmb.json

gcloud storage cp myproj/audios/ gs://input-moj-audios/**.mp3




"""Detect text in a video stored on GCS."""
import json

from google.cloud import storage
import whisper
from scipy.io import wavfile


INPUT_BUCKET="input-moj-audios"
OUTPUT_BUCKET="output-moj-audio"

def get_audio(event, context):
  model = whisper.load_model("small")
  
  print(event)

  storage_client = storage.Client(project="moj-thesis")

  input_uri = event["name"]
  file_stem = event["name"].split(".")[0]
  output_uri = f"{file_stem}.json"
  bucket = storage_client.bucket(INPUT_BUCKET)
  blob = bucket.blob(input_uri)
  with blob.open(mode="rb") as f:
    samplerate, waveform = wavfile.read(f)

  result = model.transcribe(waveform)

  bucket = storage_client.bucket(OUTPUT_BUCKET)
  blob = bucket.blob(output_uri)

  result_string = json.dumps(result)
  blob.upload_from_string(result_string)

  print("Processing audio ", input_uri)
