import xml.etree.ElementTree as ET

from pymathml import *
from pymathml.utils import identifiers, to_mml, table, underbrace


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
    rhs3 = +Sum(Fenced(p(i, j)-p[i-1, j])**2, Equals(i, 0), m-1)
    t = table([[lhs, rhs1], [None, rhs2], [None, rhs3]],
              columnspacing='0em',
              columnalign='right left',
              displaystyle='true')

    html = ET.Element('html')
    head = ET.SubElement(html, 'head')
    meta = ET.SubElement(head, 'meta', charset='utf-8')
    body = ET.SubElement(html, 'body')
    body.append(to_mml(t, display='block'))

    tree = ET.ElementTree(html)
    with open('essai.html', 'w', encoding='utf8') as f:
        tree.write(f, encoding='unicode', method='html')
