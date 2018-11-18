import os
import tempfile
from subprocess import run, PIPE

from bubblesub.api.cmd import BaseCommand
from bubblesub.ass.event import Event
from bubblesub.opt.menu import MenuCommand


class AutoTimeCommand(BaseCommand):
    names = ["auto-time"]
    help_text = (
        "Attempts to add empty subtitles on parts of audio containing speech."
    )

    @property
    def is_enabled(self):
        return self.api.media.is_loaded

    async def run(self):
        _, temp_path = tempfile.mkstemp(suffix=".wav")
        result = run(["ffmpeg", "-y", "-i", self.api.media.path, temp_path])
        if result.returncode != 0:
            self.api.log.error(result.stdout)
            return

        result = run(["auditok", "-i", temp_path], stdout=PIPE)
        if result.returncode != 0:
            self.api.log.error(result.stdout)
            return

        with self.api.undo.capture():
            for line in result.stdout.decode().split("\n"):
                if not line:
                    continue
                _line_id, start, end = line.split()
                ms_start = float(start) * 1000
                ms_end = float(end) * 1000
                self.api.subs.events.append(
                    Event(
                        start=self.api.media.video.align_pts_to_near_frame(
                            ms_start
                        ),
                        end=self.api.media.video.align_pts_to_near_frame(
                            ms_end
                        ),
                    )
                )

        os.unlink(temp_path)


COMMANDS = [AutoTimeCommand]
MENU = [MenuCommand("Auto time", "auto-time")]
