import re
from html import escape

CONTEXT_SHIFT = 60
WORD_SHIFT = 5
QUESTION_PROMPT = "Пацвердзіць замену?\n[[[ Калі вы бачыце штосьці ненармальнае, то вам здаецца ;) ]]]"

def replace_char(match, replace):
    """
    Replaces a character in a match while preserving its case.

    Args:
        match (re.Match): A regular expression match containing the character to be replaced.
        replace (str): The replacement character.

    Returns:
        str: The replacement character with the case preserved.
    """
    return (replace, replace.upper())[match.group(0).isupper()]

def find_word_boundaries(text, position):
    # Use regular expressions to find the word boundaries
    pattern = r'\W*[\b]\w+[\b]'
    matches = re.finditer(pattern, text)
    for match in matches:
        start, end = match.span()
        if start <= position <= end:
            return start, end
    return None, None

def update_text(text, rule):
    search_str, replace_str = rule
    EXCEPTIONS = ('', '’')
    if replace_str in EXCEPTIONS:
        return re.sub(search_str, replace_str, text, flags=re.IGNORECASE)
    return re.sub(search_str, lambda match: replace_char(match, replace_str), text, flags=re.IGNORECASE)

def apply_rule(text, rule, match, main_window):
    search_str, replace_str = rule

    start, end = match.span()
    segment = match.group()
    ctx_start = max(0, start - CONTEXT_SHIFT)
    ctx_end = end + CONTEXT_SHIFT
    ctx = text[ctx_start:start] + segment + text[end:ctx_end]

    # Find the word boundaries
    word_start, word_end = find_word_boundaries(text, start)
    if word_start is None:
        word_start = max(0, start - WORD_SHIFT)
    if word_end is None:
        word_end = end + WORD_SHIFT

    ctx_hl = (
        text[ctx_start:word_start]
        + f'<span style="color:yellow">{text[word_start:start]}</span>'
        + f'<span style="color:red">{segment}</span>'
        + f'<span style="color:yellow">{text[end:word_end]}</span>'
        + text[word_end:ctx_end]
    )

    replace_hl = (
        text[ctx_start:word_start]
        + f'<span style="color:green">{update_text(text[word_start:word_end], rule)}</span>'
        + text[word_end:ctx_end]
    )

    if segment in text[word_start:word_end]:
        if main_window.show_confirmation_dialog(QUESTION_PROMPT, ctx_hl, replace_hl):
            text = text[:word_start] + update_text(text[word_start:word_end], rule) + text[word_end:]
        else:
            print(f"User declined. {ctx}")

    return text

def apply_all_rules(text, rules, main_window):
    # Escape HTML-like tags to prevent truncation
    text = escape(text)

    # Convert newline characters to HTML line breaks
    text = text.replace('\n', '<br>')

    # Convert tabs to HTML entities only if not within HTML tags
    def replace_tab(match):
        return '&#09;' if not re.search(r'<[^>]*$', match.group(0)) else '\t'

    text = re.sub(r'\t+', replace_tab, text)

    for rule in rules:
        rule_tr = (rule.search_str, rule.replace_str)
        if rule.ask_flag is None:
            text = update_text(text, rule_tr)
            continue
        matches = re.finditer(rule.search_str, text, flags=re.IGNORECASE)
        for match in matches:
            text = apply_rule(text, rule_tr, match, main_window)

    return text

