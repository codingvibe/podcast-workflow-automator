# podcast-workflow-automator
A script that uploads a podcast to Buzzsprout, creates an audio visualization of your podcast, then uploads to YouTube


## Command line arguments
I know there are a lot. I'm sorry.

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| --audio | path to audio file to upload | true | N/A |
| --title | title of the uploaded podcast and video | true | N/A |
| --description | description of the podcast and video | true | N/A |
| --api-key | Buzzsprout API key to use to upload | true | N/A |
| --podcast-id | ID of the podcast to upload to | true | false |
| --background-image | path to image to use for background in video | true | N/A |
| --tags | space separated list of tags for the podcast and video | false | |
| --episode-number | episode number of this upload | false | If not supplied, most recent episode number + 1 |
| --season-number | season number for this upload | false | If not supplied, most recent episode number |
| --private | whether or not this upload should be private | false | false |
| --publish-at-date | date to publish video (format is YYYY-MM-DD) | false | |
| --publish-at-time | time to publish video (iso format) | false | |
| --explicit | whether or not this upload is explicit | false | false |
| --email-after-process | whether or not to email after processing is done | false | true |
| --category | YouTube category of video (https://developers.google.com/youtube/v3/docs/videoCategories/list) | false | 22 |
| --client-secrets-file | path to client secrets json file | false | `youtube-uploader-client-credentials.json` |
| --output-video | path and name of output file. Must end in .mp4. If not supplied, a temp name will be used and the video will be deleted after upload | false | test.mp4 |
| --vis-background-to-vid-ratio | ratio of visualization background height to input image height (0.0-1.0) | false | 0.2 |
| --vis-waves-to-vid-ratio | ratio of visualization waves height to input image height (0.0-1.0) | false | 0.15 |
| --vis-color | color for visualization waveforms. can be used multiple times | false | "0xffffff" |
| --vis-color-opacity | opacity of vis colors (0.0-1.0) | false | 0.9 |
| --background-color | background color for visualization waveforms | false | "0x000000" |
| --background-color-opacity | opacity for visualization background color (0.0-1.0) | false | 0.5 |
| --skip-podcast-upload | whether or not to skip uploading the podcast and go straight to creating/uploading the video | false | false |

## Example run
`python .\podcast-workflow.py --audio ep21.mp3 --title "Ep 21: A very good podcast episode" --description "This episode slaps." --tags "podcast" --publish-at-date 2022-02-23 --publish-at-time 11:00 --api-key <api_key> --podcast-id <podcast_id> --background-image background.png --vis-color 0x7330c9 0xffffff --youtube-client-secrets-file my-youtube-uploader-client-credentials.json --output-video ep21.mp4`