from bubblesub.cfg.menu import MenuCommand

from .command import QualityCheckCommand

COMMANDS = [QualityCheckCommand]
MENU = [MenuCommand("&Quality check", "qc")]
