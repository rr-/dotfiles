"""Draw the window frames, because xfwm4 takes pictures rather than colors.

Every other consumer here reads a rendered text file. xfwm4 reads a directory
of PNGs, so this builds them from the same roles the rest of the theme uses.

Two things about xfwm4 shape what comes out:

- it treats a theme image's alpha as a cutout, not as a blend. Anything under
  full opacity is punched out of the frame, which is why every pixel written
  here is opaque and picom is left to do all the blending (frame-opacity in
  cfg/xfce/picom.conf).
- it caches a theme's images under the theme's name, so a switch that reused
  one name would keep showing the old pictures. Each theme gets its own
  directory and `apply` moves between them, which is a name change and so a
  reload.
"""

from pathlib import Path

from PIL import Image, ImageDraw

from cfg.theme.render import THEMES, Role, load_roles, to_rgb
from libdotfiles.util import HOME_DIR

# rgba, and always fully opaque: see the note about cutouts above
Colour = tuple[int, ...]

THEMES_DIR = HOME_DIR / ".themes"
BORDER = 24
TITLE = BORDER  # a bezel the same weight the whole way round
BUTTON = 22


def theme_name(theme: str) -> str:
    return f"dash-{theme}"


def _rgba(roles: dict[str, Role], name: str, theme: str) -> Colour:
    return (*to_rgb(roles[name].color(theme)), 255)


def _slab(
    width: int, height: int, film: Colour, edge: Colour, rules: str
) -> Image.Image:
    """A slab of film carrying a 1px rule on each named side."""
    image = Image.new("RGBA", (width, height), film)
    draw = ImageDraw.Draw(image)
    if "l" in rules:
        draw.line([(0, 0), (0, height - 1)], fill=edge)
    if "r" in rules:
        draw.line([(width - 1, 0), (width - 1, height - 1)], fill=edge)
    if "t" in rules:
        draw.line([(0, 0), (width - 1, 0)], fill=edge)
    if "b" in rules:
        draw.line([(0, height - 1), (width - 1, height - 1)], fill=edge)
    return image


def _glyph(kind: str, colour: Colour, film: Colour) -> Image.Image:
    image = Image.new("RGBA", (BUTTON, BUTTON), film)
    draw = ImageDraw.Draw(image)
    near, far = 6, BUTTON - 7
    if kind == "close":
        draw.line([(near, near), (far, far)], fill=colour, width=2)
        draw.line([(near, far), (far, near)], fill=colour, width=2)
    elif kind == "maximize":
        draw.rectangle([near, near, far, far], outline=colour, width=2)
    elif kind == "hide":
        draw.line([(near, far), (far, far)], fill=colour, width=2)
    elif kind == "shade":
        draw.line([(near, near), (far, near)], fill=colour, width=2)
    elif kind == "stick":
        draw.ellipse(
            [near + 2, near + 2, far - 2, far - 2], outline=colour, width=2
        )
    else:  # menu
        draw.rectangle([near, near + 2, far, far - 2], outline=colour, width=1)
    return image


def generate(target_dir: Path = THEMES_DIR) -> None:
    """Write a theme directory per theme, both ready to switch between."""
    roles = load_roles()
    for theme in THEMES:
        out = target_dir / theme_name(theme) / "xfwm4"
        out.mkdir(parents=True, exist_ok=True)
        film = {
            "active": _rgba(roles, "pane.film", theme),
            "inactive": _rgba(roles, "pane.film_deep", theme),
        }
        edge = {
            "active": _rgba(roles, "pane.accent", theme),
            "inactive": _rgba(roles, "pane.edge", theme),
        }
        ink = _rgba(roles, "pane.ink", theme)
        faint = _rgba(roles, "pane.ink_faint", theme)
        hot = _rgba(roles, "pane.hot", theme)

        for state in ("active", "inactive"):
            paper, rule = film[state], edge[state]

            def save(image: Image.Image, name: str) -> None:
                image.save(out / f"{name}-{state}.png")

            # sides carry an outer and an inner rule; the client sits between
            save(_slab(BORDER, 32, paper, rule, "lr"), "left")
            save(_slab(BORDER, 32, paper, rule, "lr"), "right")
            save(_slab(32, BORDER, paper, rule, "tb"), "bottom")
            save(_slab(BORDER, BORDER, paper, rule, "lb"), "bottom-left")
            save(_slab(BORDER, BORDER, paper, rule, "rb"), "bottom-right")
            # the top row's inner rule spans the client and stops there: a
            # full bottom rule on a corner spills the line across the border
            corner = _slab(BORDER, TITLE, paper, rule, "lt")
            corner.putpixel((BORDER - 1, TITLE - 1), rule)
            save(corner, "top-left")
            corner = _slab(BORDER, TITLE, paper, rule, "rt")
            corner.putpixel((0, TITLE - 1), rule)
            save(corner, "top-right")
            for piece in range(1, 6):
                save(_slab(8, TITLE, paper, rule, "tb"), f"title-{piece}")

        for kind in ("menu", "stick", "shade", "hide", "maximize", "close"):
            for state, colour, paper in (
                ("active", ink, film["active"]),
                ("inactive", faint, film["inactive"]),
                ("prelight", edge["active"], film["active"]),
                ("pressed", hot, film["active"]),
            ):
                glyph = _glyph(kind, colour, paper)
                glyph.save(out / f"{kind}-{state}.png")
                if kind in ("stick", "shade", "maximize"):
                    glyph.save(out / f"{kind}-toggled-{state}.png")

        # the title is spelled in the film's own colour: xfwm4 has no way to
        # hide it, but a colour already on the frame reads as nothing
        (target_dir / theme_name(theme) / "xfwm4" / "themerc").write_text(
            "button_offset=4\n"
            "button_spacing=2\n"
            "full_width_title=true\n"
            "title_horizontal_offset=6\n"
            "title_shadow_active=false\n"
            "title_shadow_inactive=false\n"
            "show_app_icon=false\n"
            f"active_text_color={roles['pane.film'].color(theme)}\n"
            f"inactive_text_color={roles['pane.film_deep'].color(theme)}\n"
        )
