import json
from collections import namedtuple
from gui import run_gui

Rule = namedtuple('Rule', ['search_str', 'replace_str', 'ask_flag'])

def load_rules_from_json(filename):
    with open(filename, "r") as rules_file:
        rule_data = json.load(rules_file)
        return [Rule(**rule) for rule in rule_data]

if __name__ == "__main__":
    RULES = load_rules_from_json("rules.json")
    run_gui(RULES)

