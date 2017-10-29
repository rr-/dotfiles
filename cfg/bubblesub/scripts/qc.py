import re
import bubblesub.util
import bubblesub.api.cmd
import ass_tag_parser


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


class QualityCheckCommand(bubblesub.api.cmd.PluginCommand):
    name = 'grid/quality-check'
    menu_name = 'Quality check'

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
