from bubblesub.api.cmd import BaseCommand
from bubblesub.opt.menu import MenuCommand


class AlignSubtitlesToVideoFramesCommand(BaseCommand):
    names = ["align-subs-to-video-frames"]
    help_text = "Aligns subtitles to video frames."

    @property
    def is_enabled(self):
        return self.api.media.is_loaded

    async def run(self):
        with self.api.undo.capture():
            for line in self.api.subs.selected_events:
                line.start = self.api.media.video.align_pts_to_near_frame(
                    line.start
                )
                line.end = self.api.media.video.align_pts_to_near_frame(
                    line.end
                )


COMMANDS = [AlignSubtitlesToVideoFramesCommand]
MENU = [
    MenuCommand(
        "Align subtitles to &video frames", "align-subs-to-video-frames"
    )
]
