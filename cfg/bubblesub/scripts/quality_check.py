import re
import bubblesub.util
import bubblesub.api.cmd
import ass_tag_parser
import fontTools.ttLib as font_tools
from collections import defaultdict


MIN_DURATION = 250  # milliseconds
MIN_DURATION_LONG = 500 # milliseconds
MIN_GAP = 250
PUNCTUATION_INSIDE_QUOTES = 2  # 1: "inside." 2: "outside".


def _check_durations(logger, line):
    text = bubblesub.util.ass_to_plaintext(line.text)
    if not text or line.is_comment:
        return

    if line.duration < MIN_DURATION:
        logger.info(
            f'#{line.number}: duration shorter than {MIN_DURATION} ms')

    if line.duration < MIN_DURATION_LONG \
            and bubblesub.util.character_count(text) >= 8:
        logger.info(
            f'#{line.number}: '
            f'duration shorter than {MIN_DURATION_LONG} ms')

    next_line = line.next
    while next_line:
        if bubblesub.util.ass_to_plaintext(next_line.text):
            gap = next_line.start - line.end
            if gap > 0 and gap < MIN_GAP:
                logger.info(
                    f'#{line.number}+#{next_line.number}: '
                    f'gap shorter than {MIN_GAP} ms ({gap} ms)')
            return
        next_line = next_line.next


def _check_punctuation(logger, line):
    text = bubblesub.util.ass_to_plaintext(line.text)

    if text.endswith('\\N'):
        logger.info(f'#{line.number}: extra line break')

    if ' \\N' in text:
        logger.info(f'#{line.number}: space before line break')

    if '  ' in text:
        logger.info(f'#{line.number}: double space')

    if '...' in text:
        logger.info(f'#{line.number}: bad ellipsis (expected …)')
    elif re.search('[…,.!?] *[,.]', text):
        logger.info(f'#{line.number}: extra comma or dot')

    if PUNCTUATION_INSIDE_QUOTES == 1:
        if re.search(r'"[\.,…?!]', line.text):
            logger.info(f'#{line.number}: period/comma outside quotation mark')
    elif PUNCTUATION_INSIDE_QUOTES == 2:
        if re.search(r'[\.,…?!]"', line.text):
            logger.info(f'#{line.number}: period/comma inside quotation mark')

    context = re.split(r'\W+', re.sub('[.,?!"]', '', line.text.lower()))
    for word in (
        'im', 'youre', 'hes', 'shes', 'theyre', 'isnt', 'arent', 'wasnt',
        'werent', 'didnt', 'thats', 'heres', 'theres', 'wheres', 'cant',
        'dont', 'wouldnt', 'couldnt', 'shouldnt', 'hasnt', 'havent', 'ive'
    ):
        if word in context:
            logger.info(f'#{line.number}: missing apostrophe')

    if re.search(r'[-–](\\N|$)', text):
        logger.info(f'#{line.number}: bad dash (expected —)')

    if re.search(r'(^|\\N)–[^–]*$', text):
        logger.info(f'#{line.number}: dialog with just one person')

    if re.search(r'(^|\\N)(- |—)', text):
        logger.info(f'#{line.number}: bad dash (expected –)')

    if re.search(r'(^|\\N)[A-Z][a-z]{,3}-[a-z]', text):
        logger.info(f'#{line.number}: possible wrong stutter capitalization')

    if re.search(r'[\.,?!][A-Za-z]|[a-zA-Z]…[A-Za-z]', text):
        logger.info(f'#{line.number}: missing space after punctuation mark')

    if re.search(r'[\.!?]\s+[a-z]', text):
        logger.info(f'#{line.number}: lowercase letter after sentence end')


def _check_malformed_tags(logger, line):
    try:
        result = ass_tag_parser.parse_ass(line.text)
    except ass_tag_parser.ParsingError as ex:
        logger.info(f'#{line.number}: invalid syntax (%r)' % str(ex))
        return

    for item in result:
        if item['type'] != 'tags':
            continue
        for subitem in item['children']:
            if subitem['type'] == 'alignment' and subitem['legacy']:
                logger.info(f'#{line.number}: using legacy alignment tag')
            if subitem['type'] == 'comment' and len(item['children']) != 1:
                logger.info(f'#{line.number}: mixing comments with tags')


def _check_disjointed_tags(logger, line):
    if '}{' in line.text:
        logger.info(f'#{line.number}: disjointed tags')


def _check_broken_comments(logger, line):
    striped_text = bubblesub.util.ass_to_plaintext(line.text)
    if '{' in striped_text \
            or '}' in striped_text \
            or re.search('}[^{]}', line.text) \
            or re.search('{[^}]{', line.text):
        logger.info(f'#{line.number}: broken comment')


def _check_double_words(logger, line):
    text = bubblesub.util.ass_to_plaintext(line.text)

    for pair in re.finditer(r'(?<!\w)(\w+)\s+\1(?!\w)', text):
        word = pair.group(1)
        logger.info(f'#{line.number}: double word ({word})')


def _check_fonts(logger, api):
    TT_NAME_ID_FONT_FAMILY = 1
    TT_NAME_ID_FULL_NAME = 4
    TT_NAME_ID_TYPOGRAPHIC_FAMILY = 16
    TT_PLATFORM_MICROSOFT = 3

    class StyleInfo:
        def __init__(self, family, is_bold, is_italic):
            self.family = family
            self.is_bold = is_bold
            self.is_italic = is_italic
            self.used_chars = []

    class FontInfo:
        def __init__(self, font_path):
            font = font_tools.TTFont(font_path)

            self.names = []
            self.is_bold = bool(font['OS/2'].fsSelection & (1 << 5))
            self.is_italic = bool(font['OS/2'].fsSelection & 1)
            self.glyphs = set(
                chr(y[0])
                for x in font['cmap'].tables
                for y in x.cmap.items())

            for record in font['name'].names:
                if record.nameID in {
                        TT_NAME_ID_FONT_FAMILY,
                        TT_NAME_ID_FULL_NAME,
                        TT_NAME_ID_TYPOGRAPHIC_FAMILY} \
                    and record.platformID == TT_PLATFORM_MICROSOFT:
                    self.names.append(record.string.decode('utf-16-be'))

    def get_used_font_styles(api):
        results = defaultdict(set)

        styles = {style.name: style for style in api.subs.styles}
        for i, line in enumerate(api.subs.lines):
            if line.is_comment:
                continue

            family = styles[line.style].font_name
            is_bold = styles[line.style].bold
            is_italic = styles[line.style].italic
            for chunk in ass_tag_parser.parse_ass(line.text):
                if chunk['type'] == 'tags':
                    for ass_tag in chunk['children']:
                        if ass_tag['type'] == 'bold':
                            if 'enabled' in ass_tag:
                                is_bold = ass_tag['enabled']
                            else:
                                is_bold = ass_tag['weight'] > 100
                        elif ass_tag['type'] == 'italics':
                            is_italic = ass_tag['enabled']
                        elif ass_tag['type'] == 'font-name':
                            family = ass_tag['name']
                elif chunk['type'] == 'text':
                    for glyph in chunk['text']:
                        results[(family, is_bold, is_italic)].add(glyph)

        return results

    def get_fonts():
        return {
            path: FontInfo(path)
            for path in (api.subs.path.parent / '../.fonts').iterdir()
        }

    def locate_font(fonts, family, is_bold, is_italic):
        candidates = []
        for font_path, font in fonts.items():
            if family.lower() in [n.lower() for n in font.names]:
                weight = (
                    (font.is_bold == is_bold) +
                    (font.is_italic == is_italic))
                candidates.append((weight, font_path, font))
        candidates.sort(key=lambda i: -i[0])
        if not candidates:
            return None
        return candidates[0]

    results = get_used_font_styles(api)
    fonts = get_fonts()
    for font_specs, glyphs in results.items():
        font_family, is_bold, is_italic = font_specs
        logger.info(f'Checking {font_family} for {len(glyphs)} glyphs…')

        result = locate_font(fonts, font_family, is_bold, is_italic)
        if not result:
            logger.warn(f'Font not found')
            continue

        _, font_path, font = result
        errors = False
        for glyph in glyphs:
            if glyph not in font.glyphs:
                logger.warn(f'glyph not found: {glyph}')
                errors = True


class QualityCheckCommand(bubblesub.api.cmd.PluginCommand):
    name = 'grid/quality-check'
    menu_name = '&Quality check'

    @property
    def is_enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        for line in self.api.subs.selected_lines:
            _check_durations(self, line)
            _check_punctuation(self, line)
            _check_malformed_tags(self, line)
            _check_disjointed_tags(self, line)
            _check_broken_comments(self, line)
            _check_double_words(self, line)
        _check_fonts(self, self.api)