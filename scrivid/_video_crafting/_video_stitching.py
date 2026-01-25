from scrivid import errors

import os
import subprocess


def _concatenate(command):
    try:
        subprocess.run(command, capture_output=True)
    except subprocess.SubprocessError as exc:
        raise errors.InternalErrorFromFFMPEG(exc, exc.stdout, exc.stderr)


def stitch_video(temporary_directory, metadata, video_length):
    input_file = os.path.join(temporary_directory, "%06d.png")
    output_file = str(metadata.save_location / f"{metadata.video_name}.mp4")
    dimensions = f"{metadata.window_width}x{metadata.window_height}"

    # I honest to god could not tell you how I figured this out. I just
    # couldn't figure out how to make a stable result for the life of me.
    command = [
        "ffmpeg",
        "-framerate", str(metadata.frame_rate),  # INPUT SETTINGS
        "-i", str(input_file),
        "-b:v", "4M",  # # # # # # # # # # # # # # OUTPUT SETTINGS
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-s", dimensions,
        output_file
    ]

    _concatenate(command)
