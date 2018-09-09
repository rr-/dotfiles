import bubblesub.api.cmd
import bubblesub.opt.menu


class AlignSubtitlesToVideoFramesCommand(bubblesub.api.cmd.BaseCommand):
    names = ['align-subs-to-video-frames']
    help_text = 'Aligns subtitles to video frames.'

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


def register(cmd_api):
    cmd_api.register_plugin_command(
        AlignSubtitlesToVideoFramesCommand,
        bubblesub.opt.menu.MenuCommand(
            'Align subtitles to &video frames', '/align-subs-to-video-frames'
        )
    )
