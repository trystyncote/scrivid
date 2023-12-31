from pathlib import Path
import scrivid


class VisibilityIndex:
    _index_dict = {
        0: (0, 75),
        1: (75, 105),
        2: (105, 225),
        3: (225, 240),
        4: (240, 330),
        5: (330, 600)
    }

    @classmethod
    def access(cls, index):
        return cls._index_dict[index]


def create_instructions(image_directory):
    instructions = []

    for index in range(6):
        instructions.append(
            scrivid.create_image_reference(
                index,
                image_directory / f"img{index+1}.png",
                layer=index+1,
                scale=1,
                visibility=scrivid.VisibilityStatus.HIDE,
                x=0,
                y=0
            )
        )

        show_time, hide_time = VisibilityIndex.access(index)
        instructions.append(scrivid.ShowAdjustment(index, show_time))
        instructions.append(scrivid.HideAdjustment(index, hide_time))

    instructions.append(scrivid.MoveAdjustment(2, 106, scrivid.Properties(x=60, y=30), 15))
    instructions.append(scrivid.MoveAdjustment(2, 122, scrivid.Properties(x=30, y=60), 15))
    instructions.append(scrivid.MoveAdjustment(4, 270, scrivid.Properties(x=100, y=100), 15))

    return instructions


def generate(save_location, images_folder):
    metadata = scrivid.Metadata(
        frame_rate=30,
        save_location=save_location,
        video_name="scrivid_sampleVideo_final",
        window_size=(852, 480)
    )

    instructions = create_instructions(images_folder)
    scrivid.compile_video(instructions, metadata)


def main():
    save_location = Path(__file__).absolute().parent
    images_folder = save_location / "images"
    generate(save_location, images_folder)


if __name__ == "__main__":
    main()
