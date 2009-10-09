# Copyright (C) 2009 by Eric Talevich (eric.talevich@gmail.com)
# This code is part of the Biopython distribution and governed by its
# license. Please see the LICENSE file that should have been included
# as part of this package.

"""Unit tests for the Bio.Tree module.
"""


import os
import unittest
import zipfile
from itertools import izip, chain
from cStringIO import StringIO

from Bio import Tree, TreeIO
from Bio.Tree import PhyloXML


# Example PhyloXML files
EX_APAF = 'PhyloXML/apaf.xml'
EX_BCL2 = 'PhyloXML/bcl_2.xml'
EX_MADE = 'PhyloXML/made_up.xml'
EX_PHYLO = 'PhyloXML/phyloxml_examples.xml'
EX_DOLLO = 'PhyloXML/o_tol_332_d_dollo.xml'
EX_MOLLUSCA = 'PhyloXML/ncbi_taxonomy_mollusca.xml.zip'


def unzip(fname):
    """Extract a single file from a Zip archive and return a handle to it."""
    assert zipfile.is_zipfile(fname)
    z = zipfile.ZipFile(fname)
    return StringIO(z.read(z.filelist[0].filename))


class UtilTests(unittest.TestCase):
    """Tests for various Tree utility functions."""
    def test_pretty_print(self):
        """Check pretty_print by counting lines of output for each example.

        The line counts are liable to change whenever the object constructors
        change.
        """
        for source, count in izip(
                (EX_APAF, EX_BCL2, unzip(EX_MOLLUSCA),
                    # unzip(EX_METAZOA), unzip(EX_NCBI),
                    ),
                (386, 747, 16207, 214911, 648553)):
            tree = TreeIO.read(source, 'phyloxml')
            output = StringIO()
            Tree.pretty_print(tree, output)
            output.seek(0)
            self.assertEquals(len(output.readlines()), count)
            output = StringIO()
            Tree.pretty_print(tree, output, show_all=True)
            output.seek(0)
            self.assertEquals(len(output.readlines()), count)

    # TODO: display "skipped" if networkx is unavailable
    def test_to_networkx(self):
        """Tree to Graph conversion, if networkx is available."""
        tree = TreeIO.read(EX_DOLLO, 'phyloxml')
        G = Tree.to_networkx(tree)
        self.assertEqual(len(G.nodes()), 659)


class TreeTests(unittest.TestCase):
    """Tests for methods on BaseTree.Tree objects."""
    # TODO: magic: iter, len, getitem
    #       get_path
    #       common_ancestor
    #       get_leaves
    #       collapse

    def setUp(self):
        self.phylogenies = list(TreeIO.parse(EX_PHYLO, 'phyloxml'))

    def test_findall(self):
        """Clade, Phylogeny: findall() method."""
        # From the docstring example
        tree = self.phylogenies[5]
        matches = list(tree.findall(PhyloXML.Taxonomy, code='OCTVU'))
        self.assertEqual(len(matches), 1)
        self.assert_(isinstance(matches[0], PhyloXML.Taxonomy))
        self.assertEqual(matches[0].code, 'OCTVU')
        self.assertEqual(matches[0].scientific_name, 'Octopus vulgaris')
        # Iteration and regexps
        tree = self.phylogenies[10]
        for point, alt in izip(tree.findall(geodetic_datum=r'WGS\d{2}'),
                               (472, 10, 452)):
            self.assert_(isinstance(point, PhyloXML.Point))
            self.assertEqual(point.geodetic_datum, 'WGS84')
            self.assertAlmostEqual(point.alt, alt)
        # boolean filter
        for clade, name in izip(tree.findall(name=True), list('ABCD')):
            self.assert_(isinstance(clade, PhyloXML.Clade))
            self.assertEqual(clade.name, name)
        # class filter
        tree = self.phylogenies[4]
        events = list(tree.findall(PhyloXML.Events))
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].speciations, 1)
        self.assertEqual(events[1].duplications, 1)
        # integer filter
        tree = TreeIO.read(EX_APAF, 'phyloxml')
        domains = list(tree.findall(start=5))
        self.assertEqual(len(domains), 8)
        for dom in domains:
            self.assertEqual(dom.start, 5)
            self.assertEqual(dom.value, 'CARD')

    def test_findall_terminal(self):
        """Clade, Phylogeny: findall() with terminal argument."""
        def iter_len(it, count=0):
            for elem in it: count += 1
            return count
        for tree, total, extern, intern in izip(
                self.phylogenies,
                (5, 5, 6, 17, 20, 26, 6, 8, 8, 18, 14, 8, 5),
                (3, 3, 3, 3,  3,  3,  3, 3, 3, 3,  4,  3, 3),
                (2, 2, 2, 2,  2,  2,  2, 2, 2, 2,  2,  2, 2),
                ):
            self.assertEqual(iter_len(tree.findall()), total)
            self.assertEqual(iter_len(tree.findall(terminal=True)), extern)
            self.assertEqual(iter_len(tree.findall(terminal=False)), intern)

# ---------------------------------------------------------

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
