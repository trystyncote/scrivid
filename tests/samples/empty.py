import scrivid

from pathlib import Path


def get_current_directory():
    return Path(__file__).absolute().parent


def data():
    # Yes, I'm serious. This is equivalently 'default behaviour'.
    metadata = scrivid.Metadata(
        fps=12,
        video_name="testSampleResult_\'empty\'", 
        window_size=(500, 500)
    )

    directory = get_current_directory().parent / "images"
    instructions = [
        # This is a cheat to prevent the video from being one frame. Ideally,
        # I'd just return an empty list or only have a list with an element
        # that forces an extended length of the video.
        scrivid.create_image_reference(
            "HIDDEN",
            directory / "img1.png",
            layer=5,
            scale=0,
            x=-500,
            y=-500
        ),
        scrivid.HideAdjustment("HIDDEN", 0),
        scrivid.MoveAdjustment("HIDDEN", 1, scrivid.Properties(x=1), 11)
    ]

    return instructions, metadata
