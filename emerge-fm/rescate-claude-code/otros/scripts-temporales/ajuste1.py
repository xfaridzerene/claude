import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b)


rep("gancho=(43.40, 49.75)", "gancho=(43.58, 49.90)")
rep("gancho=(120.35, 126.45), tramo=(0.0, 126.60)", "gancho=(120.62, 127.00), tramo=(0.0, 127.00)")
rep('''EDITS = [(['ProHiggins,'], ["ProO'Higgins,"]), (['Provo', 'Higgins'], ["ProO'Higgins"]),
         (['Provo', 'Higgins,'], ["ProO'Higgins,"]),''',
    '''EDITS = [(['ProHiggins,'], ['Pro', "O'Higgins,"]), (['Provo', 'Higgins'], ['Pro', "O'Higgins"]),
         (['Provo', 'Higgins,'], ['Pro', "O'Higgins,"]), (['y', 'que', 'desearles'], ['y', 'desearles']),''')
rep("UNIR = [['emerge', 'fm'], ['emerge', 'fm.'], ['emerge', 'fm,']]",
    "UNIR = [['emerge', 'fm'], ['emerge', 'fm.'], ['emerge', 'fm,'], ['pro', \"o'higgins\"], ['pro', \"o'higgins,\"],\n"
    "        ['garcés', 'fruit'], ['garcés', 'fruit?'], ['garcés', 'fruit.']]")
# la última palabra de cada tramo cierra con punto (el gancho termina en coma en la fuente)
rep("""    for i, w in enumerate(out):
        if (w.get('nuevo')""", """    for i, w in enumerate(out):
        if (i + 1 == len(out) or out[i + 1].get('nuevo')) and w['p'][-1] in ',;' :
            w['p'] = w['p'][:-1] + '.'
        elif (i + 1 == len(out) or out[i + 1].get('nuevo')) and w['p'][-1].isalpha():
            w['p'] += '.'
        if (w.get('nuevo')""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
