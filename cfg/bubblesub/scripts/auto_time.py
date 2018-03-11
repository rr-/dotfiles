import os
import bisect
import tempfile
from subprocess import run, PIPE
from bubblesub.api.cmd import PluginCommand


class FadeFromBlackCommand(PluginCommand):
    name = 'edit/time'
    menu_name = '&Auto time'

    @property
    def is_enabled(self):
        return self.api.media.is_loaded

    async def run(self):
        _, temp_path = tempfile.mkstemp(suffix='.wav')
        result = run(['ffmpeg', '-y', '-i', self.api.media.path, temp_path])
        if result.returncode != 0:
            self.api.log.error(result.stdout)
            return

        result = run(['auditok', '-i', temp_path], stdout=PIPE)
        if result.returncode != 0:
            self.api.log.error(result.stdout)
            return

        for line in result.stdout.decode().split('\n'):
            if not line:
                continue
            _line_id, start, end = line.split()
            ms_start = float(start) * 1000
            ms_end = float(end) * 1000
            idx_start = bisect.bisect_left(
                self.api.media.video.timecodes, ms_start)
            idx_end = bisect.bisect_left(
                self.api.media.video.timecodes, ms_end)
            self.api.subs.lines.insert_one(
                len(self.api.subs.lines),
                start=self.api.media.video.timecodes[idx_start],
                end=self.api.media.video.timecodes[idx_end])

        os.unlink(temp_path)
