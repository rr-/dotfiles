import argparse
import shlex
import typing as T
from collections import defaultdict

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.hotkeys import HotkeyContext
from bubblesub.cfg.menu import MenuCommand, SubMenu

SHORTCUTS = [f"F{num}" for num in range(1, 13)]


class ActorsTagger:
    def __init__(self, api: Api) -> None:
        self._api = api
        self._stored_hotkeys: T.Dict[str, T.Optional[str]] = {}
        self._actors: T.Dict[str, str] = {}
        self._styles: T.Dict[str, str] = {}
        self.running = False

    def enable(self) -> None:
        if self.running:
            return
        self.running = True
        self._actors.clear()
        self._styles.clear()
        self._store_hotkeys()
        self._setup_hotkeys()

    def disable(self) -> None:
        if not self.running:
            return
        self.running = False
        self._restore_hotkeys()

    def store_style(self, sender_shortcut: str) -> None:
        self._actors.pop(sender_shortcut, None)
        self._styles.pop(sender_shortcut, None)
        try:
            sub = self._api.subs.selected_events[0]
        except LookupError:
            pass
        else:
            self._styles[sender_shortcut] = sub.style

    def store_actor(self, sender_shortcut: str) -> None:
        self._actors.pop(sender_shortcut, None)
        self._styles.pop(sender_shortcut, None)
        try:
            sub = self._api.subs.selected_events[0]
        except LookupError:
            pass
        else:
            self._actors[sender_shortcut] = sub.actor

    def apply(self, sender_shortcut: str) -> None:
        if sender_shortcut in self._actors:
            for sub in self._api.subs.selected_events:
                sub.actor = self._actors[sender_shortcut]
        if sender_shortcut in self._styles:
            for sub in self._api.subs.selected_events:
                sub.style = self._styles[sender_shortcut]

    def _setup_hotkeys(self) -> None:
        if not self.running:
            return

        def set_hotkey(shortcut, cmd_parts: T.List[str]) -> None:
            self._api.cfg.hotkeys[HotkeyContext.Global, shortcut] = " ".join(
                map(shlex.quote, cmd_parts)
            )

        for shortcut in SHORTCUTS:
            set_hotkey(shortcut, ["actors", "--apply", shortcut])
            set_hotkey(
                f"Alt+{shortcut}", ["actors", "--store-style", shortcut]
            )
            set_hotkey(
                f"Ctrl+{shortcut}", ["actors", "--store-actor", shortcut]
            )

    def _store_hotkeys(self) -> None:
        for shortcut in SHORTCUTS:
            self._stored_hotkeys[shortcut] = self._api.cfg.hotkeys[
                HotkeyContext.Global, shortcut
            ]

    def _restore_hotkeys(self) -> None:
        for shortcut, cmdline in self._stored_hotkeys.items():
            self._api.cfg.hotkeys[HotkeyContext.Global, shortcut] = cmdline


tagger: ActorsTagger = None


class ActorsCommand(BaseCommand):
    names = ["actors"]
    help_text = "Turns actors into hotkeys."

    @property
    def is_enabled(self):
        return tagger.running != (self.args.mode == "on")

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("mode", choices=["on", "off"], nargs="?")
        parser.add_argument("--store-style")
        parser.add_argument("--store-actor")
        parser.add_argument("--apply")

    async def run(self):
        if self.args.mode == "on":
            tagger.enable()
        elif self.args.mode == "off":
            tagger.disable()
        elif self.args.store_style:
            tagger.store_style(self.args.store_style)
        elif self.args.store_actor:
            tagger.store_actor(self.args.store_actor)
        elif self.args.apply:
            tagger.apply(self.args.apply)


COMMANDS = [ActorsCommand]
MENU = [
    SubMenu(
        "Actors tagging",
        [
            MenuCommand("Enable", "actors on"),
            MenuCommand("Disable", "actors off"),
        ],
    )
]


def on_load(api: Api) -> None:
    global tagger
    if tagger is None:
        tagger = ActorsTagger(api)


def on_unload(_api: Api) -> None:
    global tagger
    tagger.disable()
