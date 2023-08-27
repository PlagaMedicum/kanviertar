import re
from PyQt5.QtWidgets import QMessageBox

CONTEXT_SHIFT = 40  # Adjust this value as needed

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
    word_start = text.rfind(' ', ctx_start, start) + 1
    word_end = text.rfind(' ', end, end + CONTEXT_SHIFT) - 1
    ctx = text[ctx_start:start] + segment + text[end:end + CONTEXT_SHIFT]
    ctx_hl = (
        text[ctx_start:start]
        + f'<span style="color:red">{segment}</span>'
        + text[end:end + CONTEXT_SHIFT]
    )

    if main_window.show_confirmation_dialog("Пацвердзіць замену?", ctx_hl, update_text(ctx, rule)):
        text = text[:word_start] + update_text(text[word_start:word_end], (search_str, replace_str)) + text[word_end:]
    else:
        print(f"User declined. {ctx}")

    return text

def apply_all_rules(text, rules, main_window):
    # Convert newline characters to HTML line breaks
    text = text.replace('\n', '<br>')

    for rule in rules:
        rule_tr = (rule.search_str, rule.replace_str)
        if rule.ask_flag is None:
            text = update_text(text, rule_tr)
            continue
        matches = list(re.finditer(rule.search_str, text, flags=re.IGNORECASE))
        for match in reversed(matches):
            text = apply_rule(text, rule_tr, match, main_window)

    return text

