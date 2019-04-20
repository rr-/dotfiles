import argparse
import enum
import shlex
import typing as T
from collections import defaultdict
from dataclasses import dataclass

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.hotkeys import HotkeyContext
from bubblesub.cfg.menu import MenuCommand, SubMenu

SHORTCUTS = [f"F{num}" for num in range(1, 13)]


class MacroType(enum.Enum):
    actor = enum.auto()
    style = enum.auto()
    text = enum.auto()


@dataclass
class Macro:
    name: str
    type: MacroType
    text: str


class ActorsTagger:
    def __init__(self, api: Api) -> None:
        self._api = api
        self._previous_hotkeys: T.Dict[str, T.Optional[str]] = {}
        self._macros: T.List[StoredMacro] = []
        self.running = False

    def enable(self) -> None:
        if self.running:
            return
        self.running = True
        self._macros.clear()
        self._store_hotkeys()
        self._setup_hotkeys()

    def disable(self) -> None:
        if not self.running:
            return
        self.running = False
        self._restore_hotkeys()

    def store_macro(self, type: MacroType, name: str) -> None:
        self._macros = [macro for macro in self._macros if macro.name != name]
        try:
            sub = self._api.subs.selected_events[0]
        except LookupError:
            pass
        else:
            if type == MacroType.style:
                text = sub.style
            elif type == MacroType.text:
                text = sub.text
            elif type == MacroType.actor:
                text = sub.actor
            else:
                raise NotImplementedError("not implemented")
            self._macros.append(Macro(name=name, type=type, text=text))

    def apply_macro(self, name: str) -> None:
        for macro in self._macros:
            if macro.name == name:
                break
        else:
            return

        for sub in self._api.subs.selected_events:
            if macro.type == MacroType.style:
                sub.style = macro.text
            elif macro.type == MacroType.text:
                sub.text = macro.text
            elif macro.type == MacroType.actor:
                sub.actor = macro.text
            else:
                raise NotImplementedError("not implemented")

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
            set_hotkey(
                f"Shift+{shortcut}", ["actors", "--store-text", shortcut]
            )

    def _store_hotkeys(self) -> None:
        for base in SHORTCUTS:
            for modifier in ["", "Alt+", "Ctrl+", "Shift+"]:
                shortcut = modifier + base
                self._previous_hotkeys[shortcut] = self._api.cfg.hotkeys[
                    HotkeyContext.Global, shortcut
                ]

    def _restore_hotkeys(self) -> None:
        for shortcut, cmdline in self._previous_hotkeys.items():
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
        parser.add_argument("--store-text")
        parser.add_argument("--apply")

    async def run(self):
        if self.args.mode == "on":
            tagger.enable()
        elif self.args.mode == "off":
            tagger.disable()
        elif self.args.store_style:
            tagger.store_macro(MacroType.style, self.args.store_style)
        elif self.args.store_actor:
            tagger.store_macro(MacroType.actor, self.args.store_actor)
        elif self.args.store_text:
            tagger.store_macro(MacroType.text, self.args.store_text)
        elif self.args.apply:
            tagger.apply_macro(self.args.apply)


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
