from pymathml import *


if __name__ == '__main__':
    p, i, j, m, n = identifiers('p', 'i', 'j', 'm', 'n')
    Ep = Identifier('E')[Text('p')]

    lhs = Row(Ep(p), Operator('='))
    rhs1 = underbrace(Fenced(p[m-1, 0]-p[0, 0])**2
                      +Fenced(p[0, n-1]-p[0, 0])**2,
                      'top-left corner')
    rhs2 = +underbrace(Fenced(p[0, 0]-p[0, n-1])**2
                       +Fenced(p[m-1, n-1]-p[0, n-1])**2,
                       'top-right corner')
    t = table([[lhs, rhs1], [None, rhs2]],
              columnspacing='0em',
              columnalign='right left',
              displaystyle='true')

    with open('essai.html', 'w', encoding='utf8') as f:
        f.write('<html><body>')
        f.write(to_mml(t, display='block'))
        f.write('</body></html>')
