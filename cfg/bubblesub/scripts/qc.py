import re
import bubblesub.util
import bubblesub.api.cmd


MIN_DURATION = 250  # milliseconds
MIN_DURATION_LONG = 500 # milliseconds
MIN_GAP = 250
PUNCTUATION_INSIDE_QUOTES = 2  # 1: "inside." 2: "outside".


def _check_durations(logger, line):
    text = bubblesub.util.ass_to_plaintext(line.text)
    if not text:
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

    if ' \\N' in text:
        logger.info(f'#{line.number}: space before line break')

    if '  ' in text:
        logger.info(f'#{line.number}: double space')

    if '...' in text:
        logger.info(f'#{line.number}: bad ellipsis (expected …)')

    if re.search('… *[,.]', text):
        logger.info(f'#{line.number}: extra comma or dot after ellipsis')

    if PUNCTUATION_INSIDE_QUOTES == 1:
        if re.search('[^.][.,]"', line.text):
            logger.info(f'#{line.number}: period/comma inside quotation mark')
    elif PUNCTUATION_INSIDE_QUOTES == 1:
        if re.search('"[.,][^.]', line.text) or re.search('"[.,]$', line.text):
            logger.info(f'#{line.number}: period/comma outside quotation mark')

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


def _check_malformed_tags(logger, line):
    tags3 = {'pos', 'move', 'org', 'fad'}

    def _validate_color(text):
        return re.match('^&H[0-9A-Fa-f]{6}&$', text)

    def _validate_opacity(text):
        return re.match('^&H[0-9A-Fa-f]{2}&$', text)

    def _validate_boolean(text):
        return text in '01'

    def _validate_integer(text, allow_negative):
        if allow_negative:
            return re.match(r'^\d+$', text)
        return re.match(r'^\d+$', text)

    def _validate_float(text, allow_negative):
        if allow_negative:
            return re.match(r'^-?\d+(\.\d+)?$', text)
        return re.match(r'^\d+(\.\d+)?$', text)

    if r'\}' in line.text:
        logger.info(f'#{line.number}: malformed tag (slash before brace)')

    if r'{\\' in line.text:
        logger.info(f'#{line.number}: malformed tag (double slash)')

    if re.match('{[^}]+$', line.text):
        logger.info(f'#{line.number}: malformed tag (unterminated brace)')

    for match in re.finditer(r'\\([0-9]*[a-z]+)([^\\}]*)[\\}]', line.text):
        tag = match.group(1)
        arg = match.group(2)
        if tag in (
            'n',  # soft line break
            'N',  # hard line break
            'h',  # hard space
        ):
            if arg:
                logger.info(
                    f'#{line.number}: '
                    f'malformed {tag} tag (expected no arguments)')

        elif tag in (
            'i',  # italics
            'u',  # underline
            's',  # strike-through
        ):
            if _validate_boolean(arg):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (not a boolean)')

        elif tag == 'an':  # new style anchors
            if arg not in '123456789':
                logger.info(
                    f'#{line.number}: malformed {tag} tag (bad alignment)')

        elif tag == 'a':  # old style anchors
            if arg not in ('1', '2', '3', '5', '6', '7', '9', '10', '11'):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (bad alignment)')

        elif tag == 'q':  # wrap style
            if arg not in ('1', '2', '3', '4'):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (bad wrap style)')

        elif tag in (
            'b'      # bold (weights)
            'be',    # blur edges
            'fs',    # font scale
            'fscx',  # font scale x
            'fscy',  # font scale y
            'fe',    # font encoding
            'k',     # karaoke
            'K',     # karaoke (sweep)
            'ko',    # karaoke (sweep)
            'kf',    # karaoke (sweep + hide borders)
        ):
            if not _validate_integer(arg, allow_negative=False):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (not an integer)')

        elif tag in (
            'shad',   # shadow
            'blur',   # blur
            'bord',   # border
            'xbord',  # border x
            'ybord',  # border y
        ):
            if not _validate_float(arg, allow_negative=False):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (not a number)')

        elif tag in (
            'xshad',  # shadow x
            'yshad',  # shadow y
            'fsp',    # font kerning
            'frx',    # font rotation x
            'fry',    # font rotation y
            'frz',    # font rotation z
            'fax',    # font shear x
            'fay',    # font shear y
        ):
            if not _validate_float(arg, allow_negative=True):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (not a number)')

        elif tag in ('c', '1c', '2c', '3c', '4c'):  # colors
            if not _validate_color(arg):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (not a color)')

        elif tag in ('alpha', '1a', '2a', '3a', '4a'):  # alpha
            if not _validate_opacity(arg):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (not an opacity)')

        elif tag in ('pos', 'move', 'org', 'fad', 'fade'):
            if not arg.startswith('(') or not arg.endswith(')'):
                logger.info(
                    f'#{line.number}: malformed {tag} tag (missing braces)')
            else:
                arg = arg[1:-1]
                parts = arg.split(',')
                if not all(
                        _validate_integer(part, allow_negative=True)
                        for part in parts):
                    logger.info(
                        f'#{line.number}: '
                        f'malformed {tag} tag (not an integer)')
                if tag == 'fade':
                    expected_part_count = (7,)
                elif tag == 'move':
                    expected_part_count = (4, 6)
                else:
                    expected_part_count = (2,)
                if len(parts) not in expected_part_count:
                    logger.info(
                        f'#{line.number}: '
                        f'malformed {tag} tag (invalid part count)')

        elif tag not in (
            'fn',     # font name
            'r',      # reset style
            't',      # animated transform
            'clip',   # clip path
            'iclip',  # mask path (inverse clip)
            # TODO: drawing tags
        ):
            logger.info(f'#{line.number}: unknown tag ({tag})')


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


class QualityCheckCommand(bubblesub.api.cmd.PluginCommand):
    name = 'grid/quality-check'
    menu_name = 'Quality check'

    def enabled(self):
        return self.api.subs.has_selection

    async def run(self):
        for line in self.api.subs.selected_lines:
            _check_durations(self, line)
            _check_punctuation(self, line)
            _check_malformed_tags(self, line)
            _check_disjointed_tags(self, line)
            _check_broken_comments(self, line)
            _check_double_words(self, line)
