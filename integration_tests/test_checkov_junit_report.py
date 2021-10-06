import unittest
import os
import xml.etree.ElementTree as ET

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovJunitReport(unittest.TestCase):
    def test_terragoat_junit_report(self):

        report_path = os.path.join(os.path.dirname(current_dir), 'checkov_report_terragoat.xml')
        tree = ET.parse(report_path)
        root = tree.getroot()
        self.assertEqual(root.attrib['errors'], '0')
