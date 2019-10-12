from typing import List

from prompt_toolkit import prompt

from models.track import Track


def prompt_for_input(original: Track, options: List[Track]):
    if not options:
        return None

    num_options = len(options) + 1

    formatted_options = [
        f'{idx})    {option.pretty_string()}'
        for idx, option in enumerate(options, 1)
    ]
    formatted_options.append(f'{num_options})    None')
    options_string = "\n".join(formatted_options)
    prompt_string = f'\nPlease select the most likely match for the following track:' \
                    f'\n{original.pretty_string()}\n' \
                    f'\n{options_string}\n'

    index = _safe_prompt(prompt_string, num_options)

    if not index == num_options:
        return options[index - 1]

    return None


def _safe_prompt(prompt_string, num_options):
    result = -1
    help_string = f'\nThat wasn\'t an option, dummy. Select a number between 1 and {num_options}\n'

    try:
        result = int(prompt(prompt_string))
    except ValueError:
        # Just let the error get printed once below
        pass

    while result < 1 or result > num_options:
        print(help_string)

        try:
            result = int(prompt(prompt_string))
        except ValueError:
            pass

    return result


if __name__ == '__main__':
    o = Track({}, 'a', 'b', 'c')
    opt = [
        {},
        Track({}, 'a', 'B', 'c'),
        Track({}, 'A', 'BB', 'cccc'),
        Track({}, 'A', 'dsadsad', 'ewq'),
        Track({}, 'A', 'BB', 'dsa'),
        Track({}, 'ewqsaA', 'BB', 'cccc'),
    ]
    prompt_for_input(o, opt)
