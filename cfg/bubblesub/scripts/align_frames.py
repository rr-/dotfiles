import os
from bisect import bisect_left
from bubblesub.api.cmd import PluginCommand


class FadeFromBlackCommand(PluginCommand):
    name = 'edit/align-subtitles-to-video-frames'
    menu_name = 'Align subtitles to &video frames'

    @property
    def is_enabled(self):
        return self.api.media.is_loaded

    async def run(self):
        for line in self.api.subs.selected_lines:
            idx_start = bisect_left(self.api.media.video.timecodes, line.start)
            idx_end = bisect_left(self.api.media.video.timecodes, line.end)
            line.start = self.api.media.video.timecodes[idx_start]
            line.end = self.api.media.video.timecodes[idx_end]
