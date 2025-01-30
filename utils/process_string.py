import re


def process_name(name: str) -> str:
    # Use a regular expression to find dashes between numbers
    pattern = r'(\d)-(\d)'
    replace = r'\1$-$\2'
    new_name = re.sub(pattern, replace, name)

    return new_name


def get_short_id(name: str) -> str:
    # Use a regular expression to search and extract source IDs that is formatted as <SURVEY_NAME> JHHMMSS.S[+,-]DDMMSS
    pattern = r'(J[^+-]*)'
    match = re.search(pattern, name)

    if match:
        return match.group(1)

    else:
        print(f"No match found in {name}.")


def wrap_sign(dec_str: str) -> str:
    pattern = r'([-+])'
    repl = r'$\1$'
    return re.sub(pattern, repl, dec_str)


def main() -> None:
    test = "-53:10:01.1"
    print(wrap_sign(test))


if __name__ == "__main__":
    main()
