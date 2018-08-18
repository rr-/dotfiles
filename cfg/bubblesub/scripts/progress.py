import bubblesub.api.cmd
import bubblesub.opt


def ms_to_str(ms: int) -> str:
    return str(ms // 1000)


class ProgressCommand(bubblesub.api.cmd.BaseCommand):
    names = ['progress']
    menu_name = 'Show translation &progress'
    help_text = 'How much left'

    async def run(self):
        empty_count = 0
        empty_duration = 0
        total_count = 0
        total_duration = 0
        for event in self.api.subs.events:
            if 'karaoke' in event.actor:
                continue
            total_duration += event.duration
            total_count += 1
            if not event.text:
                empty_duration += event.duration
                empty_count += 1

        self.api.log.info(
            f'{empty_count} lines left ('
            f'{total_count-empty_count}/{total_count}, '
            f'{(total_count-empty_count)/total_count:.01%})'
        )
        self.api.log.info(
            f'{ms_to_str(empty_duration)} seconds left ('
            f'{ms_to_str(total_duration-empty_duration)}/'
            f'{ms_to_str(total_duration)}, '
            f'{(total_duration-empty_duration)/total_duration:.01%})'
        )


def register(cmd_api):
    cmd_api.register_plugin_command(
        ProgressCommand,
        bubblesub.opt.menu.MenuCommand('/progress')
    )
