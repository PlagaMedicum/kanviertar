import re
import json
from collections import namedtuple

Rule = namedtuple('Rule', ['search_str', 'replace_str', 'ask_flag'])

CONTEXT_SHIFT = 40
WORD_SHIFT = 5

def highlight_text(text):
    """
    Highlights a given text using ANSI escape codes for red text.
    """
    return f'\033[1;31m{text}\033[m'

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

def apply_rule(text, rule):
    search_str, replace_str, ask_flag = rule

    if ask_flag is None:
        return update_text(text, (search_str, replace_str))

    for match in re.finditer(search_str, text, flags=re.IGNORECASE):
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

        prompt = f"> Пацвердзіць замену?\n{ctx}\nБудзе заменена на: {replace_str}\n(н/не/n/nie/no, каб адхіліць замену): "
        try:
            response = input(prompt).strip().lower()
            if response in ('н', 'не', 'n', 'nie', 'no'):
                continue
            text = text[:word_start] + update_text(text[word_start:word_end], (search_str, replace_str)) + text[word_end:]
        except KeyboardInterrupt:
            print('\nКарыстальнік перапыніў аперыцыю.')
            return text

    return text

def main():
    prompt = 'Увядзіце тэкст для канвертацыі:\n'
    try:
        text = input(prompt)
    except KeyboardInterrupt:
        print('\nКарыстальнік перапыніў аперыцыю.')

    with open('rules.json', 'r') as rules_file:
        rule_data = json.load(rules_file)
        RULES = [Rule(**rule) for rule in rule_data]

    new_text = text

    for rule in RULES:
        new_text = apply_rule(new_text, rule)

    print(f"\n! Канвертаваны тэкст (Увага! Тэкст можа патрабаваць дадатковай вычыткі):\n{new_text}")
    # prompt = f"\nСкапіяваць тэкст у буфер абмену?\n(так/т/tak/t/yes/y)))"
    # try:
    #     response = input(prompt).strip().lower()
    #     if response in ('т', 'так', 't', 'tak', 'y', 'yes'):
    #         pyperclip.copy(new_text)
    # except KeyboardInterrupt:
    #     print('\nКарыстальнік перапыніў аперыцыю.')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Адбылася памылка: ', e)

