from pathlib import Path
import scrivid


def create_instruction(index, show_time, hide_time, instructions, image_directory):
    instructions.append(
        scrivid.create_image_reference(
            index,
            image_directory / f"img{index+1}.png",
            layer=index+1,
            scale=1,
            visibility=scrivid.properties.VisibilityStatus.HIDE,
            x=0,
            y=0
        )
    )
    instructions.append(scrivid.adjustments.show.create(index, show_time))
    instructions.append(scrivid.adjustments.hide.create(index, hide_time))


def create_all_instructions(image_directory):
    instructions = []
    visibility_times = [
        (0, 75),
        (75, 105),
        (105, 225),
        (225, 240),
        (240, 330),
        (330, 600)
    ]

    for index, visibility_time in enumerate(visibility_times):
        create_instruction(index, *visibility_time, instructions, image_directory)

    instructions.append(scrivid.adjustments.move.create(2, 106, scrivid.properties.Properties(x=60, y=30), 15))
    instructions.append(scrivid.adjustments.move.create(2, 122, scrivid.properties.Properties(x=30, y=60), 15))
    instructions.append(scrivid.adjustments.move.create(4, 270, scrivid.properties.Properties(x=100, y=100), 15))

    return instructions


def generate(save_location, images_folder):
    metadata = scrivid.Metadata(
        frame_rate=30,
        save_location=save_location,
        video_name="scrivid_sampleVideo_final",
        window_size=(852, 480)
    )

    instructions = create_all_instructions(images_folder)
    scrivid.compile_video(instructions, metadata)


def main():
    save_location = Path(__file__).absolute().parent
    images_folder = save_location / "images"
    generate(save_location, images_folder)


if __name__ == "__main__":
    main()
