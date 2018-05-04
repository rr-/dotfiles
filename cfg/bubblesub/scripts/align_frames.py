from bisect import bisect_left

import bubblesub.api.cmd
import bubblesub.opt.menu


class AlignSubtitlesToVideoFramesCommand(bubblesub.api.cmd.BaseCommand):
    name = 'plugin/align-subs-to-video-frames'
    menu_name = 'Align subtitles to &video frames'

    @property
    def is_enabled(self):
        return self.api.media.is_loaded

    async def run(self):
        with self.api.undo.capture():
            for line in self.api.subs.selected_lines:
                idx_start = bisect_left(
                    self.api.media.video.timecodes, line.start
                )
                idx_end = bisect_left(self.api.media.video.timecodes, line.end)
                line.start = self.api.media.video.timecodes[idx_start]
                line.end = self.api.media.video.timecodes[idx_end]


def register(cmd_api):
    cmd_api.register_plugin_command(
        AlignSubtitlesToVideoFramesCommand,
        bubblesub.opt.menu.MenuCommand(
            AlignSubtitlesToVideoFramesCommand.name
        )
    )
