#!/usr/bin/python
import argparse
import datetime
import errno
import ffmpeg
import os
import pytz
import sys

from buzzsprout_uploader import upload_podcast
from audio_to_visualization import create_visualization
from youtube_uploader import upload_video


TEMP_FILENAME = 'temp.mp4'


def valid_date(s):
  try:
    return datetime.date.fromisoformat(s)
  except ValueError:
    msg = "not a valid date: {0!r}".format(s)
    raise argparse.ArgumentTypeError(msg)


def valid_time(s):
  try:
    return datetime.time.fromisoformat(s)
  except ValueError:
    msg = "not a valid time: {0!r}".format(s)
    raise argparse.ArgumentTypeError(msg)


# Arg validation for floats
def restricted_float(x):
  try:
    x = float(x)
  except ValueError:
    raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

  if x < 0.0 or x > 1.0:
    raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
  return x

# python .\podcast-workflow.py --audio C:\Users\colby\Music\GoGettas\ep20.mp3 --title "Ep 20: Dr Strange and The Yeti Mines of Canada" --description "Okay, but seriously, why is Cyclops the absolute worst in every live action movie. #JusticeForScott" --tags "gogettas" "Marvel" "Dr.Strange" --publish-at-date 02/23/2022 --publish-at-time 11:00 --api-key 36ab379f9970999001f566c4639837ef --podcast-id 1870685 --background-image C:\Users\colby\Pictures\youtube-background-2.png --vis-color 0x7330c9 0xffffff --youtube-client-secrets-file C:\Users\colby\Documents\stream-projects\youtube-uploader\youtube-uploader-client-credentials.json

def create_podcast_with_args():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=True)
  parser.add_argument("--audio",
                      help="input audio filename", required=True)
  parser.add_argument("--title",
                      help="title of the podcast", required=True)
  parser.add_argument("--description",
                      help="description of the podcast", required=True)
  parser.add_argument("--tags", nargs='*',
                      help="tags for the episode", required=False)
  parser.add_argument("--publish-at-date", type=valid_date,
                      help="date to publish the podcast", required=False)
  parser.add_argument("--publish-at-time", type=valid_time, required=False,
                      help="time to publish the podcast")
  parser.add_argument("--episode-number", type=int, required=False,
                      help="episode number of podcast (if none, most recent ep number +1)")
  parser.add_argument("--season-number", type=int, required=False,
                      help="season number of podcast (if none, season number of most recent episode")
  parser.add_argument("--private", type=bool, default=False,
                      help="whether or not podcast is private", required=False)
  parser.add_argument("--explicit", type=bool, default=False,
                      help="whether or not podcast is explicit", required=False)
  parser.add_argument("--email-after-process", type=bool, default=True,
                      help="whether or not to email after the processing is done", required=False)
  parser.add_argument("--api-key",
                      help="API key to use when calling Buzzsprout", required=True)
  parser.add_argument("--podcast-id",
                      help="ID of podcast to upload to", required=True)
  parser.add_argument("--skip-podcast-upload", help="Skip uploading of podcast",
                      action='store_true', default=False)
  parser.add_argument("--background-image",
                      help="visualization background filename", required=True)
  parser.add_argument("--output-video", help="output video filename",
                      required=False, default=TEMP_FILENAME)
  parser.add_argument("--vis-background-to-vid-ratio", type=restricted_float, default=0.2,
                      help="ratio of visualization background height to input image height (0.0-1.0)", required=False)
  parser.add_argument("--vis-waves-to-vid-ratio", type=restricted_float, default=0.15,
                      help="ratio of visualization waves height to input image height (0.0-1.0)", required=False)
  parser.add_argument("--vis-color", nargs='*', required=False, default=["0xffffff"],
                      help="colors for visualization waveforms")
  parser.add_argument("--vis-color-opacity", type=restricted_float, default=0.9,
                      help="opacity of vis colors (0.0-1.0)", required=False)
  parser.add_argument("--background-color", required=False, default="0x000000",
                      help="background color for visualization waveforms")
  parser.add_argument("--background-color-opacity", type=restricted_float, default=0.5,
                      help="opacity for visualization background color (0.0-1.0)", required=False)
  parser.add_argument("--youtube-category", default="22",
    help="Numeric video category. " +
      "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
  parser.add_argument("--youtube-client-secrets-file", help="Path to client secrets json file",
                      default="youtube-uploader-client-credentials.json", required=False)

  args, _ = parser.parse_known_args()

  # Compile the publish time if applicable
  publish_at = None
  if (args.publish_at_date is not None and args.publish_at_time is None) or \
     (args.publish_at_date is None and args.publish_at_time is not None):
     exit("Must specify both publish_at date and time for scheduling")

  if args.publish_at_date is not None:
    publish_at = datetime.datetime.combine(args.publish_at_date, args.publish_at_time)
    publish_at = pytz.utc.localize(publish_at)
  
  if publish_at < pytz.utc.localize(datetime.datetime.now()):
    exit("Must specify a time in the future")

  create_podcast(args.audio, args.title, args.description, args.tags, publish_at,
                 args.episode_number, args.season_number, args.private, args.explicit,
                 args.email_after_process, args.api_key, args.podcast_id, args.skip_podcast_upload,
                 args.background_image, args.output_video, args.vis_background_to_vid_ratio,
                 args.vis_waves_to_vid_ratio, args.vis_color, args.vis_color_opacity,
                 args.background_color, args.background_color_opacity, args.youtube_category,
                 args.youtube_client_secrets_file)


def create_podcast(audio, title, description, tags, publish_at,
                   episode_number, season_number, private, explicit,
                   email_after_process, api_key, podcast_id, skip_podcast_upload,
                   background_image, output_video, vis_background_to_vid_ratio,
                   vis_waves_to_vid_ratio, vis_color, vis_color_opacity,
                   background_color, background_color_opacity, youtube_category,
                   youtube_client_secrets_file):
  if not skip_podcast_upload:
    upload_podcast(audio, title, description, tags, publish_at, episode_number, season_number,
                   private, explicit, email_after_process, api_key, podcast_id)
  
  try: 
    create_visualization(audio, background_image, output_video, vis_background_to_vid_ratio,
                          vis_waves_to_vid_ratio, vis_color, vis_color_opacity,
                          background_color, background_color_opacity)
  except ffmpeg.Error as e:
    print("No overwriting, proceeding with caution")
  
  privacy_status = "private" if private else "public"
  if publish_at is not None:
    privacy_status = "private"
  upload_video(output_video, title, description, youtube_category, ",".join(tags),
               privacy_status, publish_at, youtube_client_secrets_file)
  
  if output_video == TEMP_FILENAME:
    os.remove(output_video)


if __name__ == "__main__":
  try:
    create_podcast_with_args()
  except KeyboardInterrupt:
    # The user asked the program to exit
    sys.exit(1)
  except IOError as e:
    # When this program is used in a shell pipeline and an earlier program in
    # the pipeline is terminated, we'll receive an EPIPE error.  This is normal
    # and just an indication that we should exit after processing whatever
    # input we've received -- we don't consume standard input so we can just
    # exit cleanly in that case.
    if e.errno != errno.EPIPE:
      raise

    # We still exit with a non-zero exit code though in order to propagate the
    # error code of the earlier process that was terminated.
    sys.exit(1)

  sys.exit(0)
