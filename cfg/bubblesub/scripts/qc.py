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
        logger.info('#{}: duration shorter than {} ms'.format(
            line.number, MIN_DURATION))

    if line.duration < MIN_DURATION_LONG \
            and bubblesub.util.character_count(text) >= 8:
        logger.info('#{}: duration shorter than {} ms'.format(
            line.number, MIN_DURATION_LONG))

    next_line = line.next
    while next_line:
        if bubblesub.util.ass_to_plaintext(next_line.text):
            gap = next_line.start - line.end
            if gap > 0 and gap < MIN_GAP:
                logger.info('#{}+#{}: gap shorter than {} ms ({} ms)'.format(
                    line.number, next_line.number, MIN_GAP, gap))
            return
        next_line = next_line.next


def _check_punctuation(logger, line):
    text = bubblesub.util.ass_to_plaintext(line.text)

    if ' \\N' in text:
        logger.info('#{}: space before line break'.format(line.number))

    if '  ' in text:
        logger.info('#{}: double space'.format(line.number))

    if '...' in text:
        logger.info('#{}: bad ellipsis (expected …)'.format(line.number))

    if re.search('… *[,.]', text):
        logger.info('#{}: comma or dot after ellipsis'.format(line.number))

    if PUNCTUATION_INSIDE_QUOTES == 1:
        if re.search('[^.][.,]"', line.text):
            logger.info('#{}: period/comma inside quotation mark'.format(
                line.number))
    elif PUNCTUATION_INSIDE_QUOTES == 1:
        if re.search('"[.,][^.]', line.text) or re.search('"[.,]$', line.text):
            logger.info('#{}: period/comma outside quotation mark'.format(
                line.number))

    context = re.split(r'\W+', re.sub('[.,?!"]', '', line.text.lower()))
    for word in (
        'im', 'youre', 'hes', 'shes', 'theyre', 'isnt', 'arent', 'wasnt',
        'werent', 'didnt', 'thats', 'heres', 'theres', 'wheres', 'cant',
        'dont', 'wouldnt', 'couldnt', 'shouldnt', 'hasnt', 'havent', 'ive'
    ):
        if word in context:
            logger.info('#{}: missing apostrophe'.format(line.number))

    if re.search(r'[-–](\\N|$)', text):
        logger.info('#{}: bad dash (expected —)'.format(line.number))

    if re.search(r'(^|\\N)–[^–]*$', text):
        logger.info('#{}: dialog with just one person'.format(line.number))

    if re.search(r'(^|\\N)(- |—)', text):
        logger.info('#{}: bad dash (expected –)'.format(line.number))

    if re.search(r'(^|\\N)[A-Z][a-z]{,3}-[a-z]', text):
        logger.info('#{}: wrong stutter capitalization'.format(line.number))


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
        logger.info('#{}: malformed tag (slash before brace)'.format(
            line.number))

    if r'{\\' in line.text:
        logger.info('#{}: malformed tag (double slash)'.format(line.number))

    if re.match('{[^}]+$', line.text):
        logger.info('#{}: malformed tag (unterminated brace)'.format(
            line.number))

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
                    '#{}: malformed {} tag (expected no arguments)'.format(
                        line.number, tag))

        elif tag in (
            'i',  # italics
            'u',  # underline
            's',  # strike-through
        ):
            if _validate_boolean(arg):
                logger.info('#{}: malformed %s tag (not a boolean)'.format(
                    line.number, tag))

        elif tag == 'an':  # new style anchors
            if arg not in '123456789':
                logger.info('#{}: malformed %s tag (bad alignment)'.format(
                    line.number, tag))

        elif tag == 'a':  # old style anchors
            if arg not in ('1', '2', '3', '5', '6', '7', '9', '10', '11'):
                logger.info('#{}: malformed %s tag (bad alignment)'.format(
                    line.number, tag))

        elif tag == 'q':  # wrap style
            if arg not in ('1', '2', '3', '4'):
                logger.info('#{}: malformed %s tag (bad wrap style)'.format(
                    line.number, tag))

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
                logger.info('#{}: malformed %s tag (not an integer)'.format(
                    line.number, tag))

        elif tag in (
            'shad',   # shadow
            'blur',   # blur
            'bord',   # border
            'xbord',  # border x
            'ybord',  # border y
        ):
            if not _validate_float(arg, allow_negative=False):
                logger.info('#{}: malformed %s tag (not a number)'.format(
                    line.number, tag))

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
                logger.info('#{}: malformed %s tag (not a number)'.format(
                    line.number, tag))

        elif tag in ('c', '1c', '2c', '3c', '4c'):  # colors
            if not _validate_color(arg):
                logger.info('#{}: malformed {} tag (not a color)'.format(
                    line.number, tag))

        elif tag in ('alpha', '1a', '2a', '3a', '4a'):  # alpha
            if not _validate_opacity(arg):
                logger.info('#{}: malformed {} tag (not an opacity)'.format(
                    line.number, tag))

        elif tag in ('pos', 'move', 'org', 'fad', 'fade'):
            if not arg.startswith('(') or not arg.endswith(')'):
                logger.info(
                    '#{}: malformed {} tag (missing braces)'.format(
                        line.number, tag))
            else:
                arg = arg[1:-1]
                parts = arg.split(',')
                if not all(
                        _validate_integer(part, allow_negative=True)
                        for part in parts):
                    logger.info(
                        '#{}: malformed {} tag (not an integer)'.format(
                            line.number, tag))
                if tag == 'fade':
                    expected_part_count = (7,)
                elif tag == 'move':
                    expected_part_count = (4, 6)
                else:
                    expected_part_count = (2,)
                if len(parts) not in expected_part_count:
                    logger.info(
                        '#{}: malformed {} tag (invalid part count)'.format(
                            line.number, tag))

        elif tag not in (
            'fn',     # font name
            'r',      # reset style
            't',      # animated transform
            'clip',   # clip path
            'iclip',  # mask path (inverse clip)
            # TODO: drawing tags
        ):
            logger.info(
                '#{}: unknown tag ({})'.format(line.number, tag))


def _check_disjointed_tags(logger, line):
    if '}{' in line.text:
        logger.info('#{}: disjointed tags'.format(line.number))


def _check_broken_comments(logger, line):
    striped_text = bubblesub.util.ass_to_plaintext(line.text)
    if '{' in striped_text \
            or '}' in striped_text \
            or re.search('}[^{]}', line.text) \
            or re.search('{[^}]{', line.text):
        logger.info('#{}: broken comment'.format(line.number))


def _check_double_words(logger, line):
    text = bubblesub.util.ass_to_plaintext(line.text)

    for pair in re.finditer(r'(?<!\w)(\w+)\s+\1(?!\w)', text):
        logger.info('#{}: double word ({})'.format(
            line.number, pair.group(1)))


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
