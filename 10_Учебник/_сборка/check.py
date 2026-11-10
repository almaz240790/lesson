#!/usr/bin/env python3
"""Проверка главы учебника: python3 check.py <глава.md> [...]. Код возврата 1, если есть ошибки."""
import os
import re
import sys

BANNED = [
    'важно отметить', 'стоит отметить', 'стоит подчеркнуть', 'следует отметить', 'как известно',
    'в этой главе мы', 'давайте разбер', 'давайте рассмотр', 'не секрет, что', 'в заключение',
    'гарантирует прибыль', 'гарантированн', 'безошибочн', 'беспроигрышн',
]
TF_BAD = re.compile(r'\b(?:M1|M5|M15|M30|H1|H4|D1|W1|MN)\b')


def check(path):
    errs, warns = [], []
    text = open(path, encoding='utf-8').read()
    base = os.path.dirname(os.path.abspath(path))
    lines = text.split('\n')

    # блоки кода исключаем из большинства проверок
    in_code = False
    prose = []
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith('```'):
            in_code = not in_code
            continue
        if not in_code:
            prose.append((n, line))
    if in_code:
        errs.append('не закрыт блок кода ```')

    if not lines or not re.match(r'^# Глава \d+\. \S', lines[0]):
        errs.append('первая строка должна быть «# Глава N. Название»')
    m = re.match(r'^# Глава (\d+)\.', lines[0]) if lines else None
    num = m.group(1) if m else None

    for n, line in prose:
        stripped = re.sub(r'`[^`]*`', '', line)
        if re.search(r'<!--|</?[a-zA-Z][a-zA-Z0-9]*(\s[^<>]*)?/?>', stripped):
            errs.append(f'{n}: HTML в тексте: {line.strip()[:80]}')
        if re.search(r'\$\$|\\frac|\\times|\\text\{', stripped):
            errs.append(f'{n}: LaTeX в тексте')
        low = stripped.lower()
        for b in BANNED:
            if b in low:
                warns.append(f'{n}: штамп или запрещённое слово «{b}»')
        if TF_BAD.search(stripped):
            warns.append(f'{n}: обозначение таймфрейма не по канону: {TF_BAD.search(stripped).group(0)}')
        for m2 in re.finditer(r'!?\[([^\]]*)\]\(([^)\s]+)\)', stripped):
            target = m2.group(2)
            if re.match(r'^(https?:|mailto:|#)', target):
                continue
            p = os.path.normpath(os.path.join(base, target.split('#')[0]))
            if not os.path.exists(p):
                errs.append(f'{n}: ссылка на несуществующий файл: {target}')
        if num and re.match(r'^## ', line) and not re.match(rf'^## ({num}\.\d+\. |Источники\s*$)', line):
            errs.append(f'{n}: заголовок раздела не «## {num}.k. Название»: {line.strip()[:60]}')

    # таблицы: одинаковое число столбцов
    i = 0
    while i < len(prose):
        n, line = prose[i]
        if line.strip().startswith('|') and i + 1 < len(prose) and re.match(r'^\s*\|[\s:|-]+\|\s*$', prose[i + 1][1]):
            cols = len(re.split(r'(?<!\\)\|', line.strip().strip('|')))
            j = i
            while j < len(prose) and prose[j][1].strip().startswith('|'):
                c = len(re.split(r'(?<!\\)\|', prose[j][1].strip().strip('|')))
                if c != cols:
                    errs.append(f'{prose[j][0]}: в строке таблицы {c} столбцов вместо {cols}')
                j += 1
            i = j
        else:
            i += 1

    heads = [l for _, l in prose if l.startswith('## ')]
    for must in ('Типичные ошибки', 'Запомнить', 'Практика на демосчёте', 'Вопросы для самопроверки', 'Ответы'):
        if not any(must in h for h in heads):
            errs.append(f'нет раздела «{must}»')
    if not any(l.startswith('> После этой главы вы умеете') for _, l in prose):
        errs.append('нет строки «> После этой главы вы умеете: …»')
    if not any(l.startswith('**Связь с курсом:**') for _, l in prose):
        errs.append('нет строки «**Связь с курсом:** …»')

    figs = re.findall(r'!\[[^\]]*\]\((img/[^)]+)\)', text)
    for f in figs:
        if not re.match(r'^img/\d\d-[a-z0-9-]+\.svg$', f):
            errs.append(f'имя рисунка не по правилу img/NN-slug.svg: {f}')
    words = len(re.findall(r'[A-Za-zА-Яа-яЁё0-9]+', ' '.join(l for _, l in prose)))
    print(f'{os.path.basename(path)}: слов {words}, рисунков {len(figs)}, ошибок {len(errs)}, замечаний {len(warns)}')
    for e in errs:
        print('  ОШИБКА', e)
    for w in warns:
        print('  замечание', w)
    return not errs


if __name__ == '__main__':
    ok = all([check(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
