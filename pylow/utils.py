from typing import List

def make_unique_string_list(content: List[str]):
    s = set()
    new = []
    for word in content:
        i = 0
        while word in s:
            word = f' {word}' if i % 2 == 0 else f'{word} '
            i += 1
        s.add(word)
        new.append(word)
    return new
