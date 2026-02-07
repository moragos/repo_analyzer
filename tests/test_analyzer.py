import unittest
import os
import tempfile
import shutil
from cpp_parser import parse_cpp_file
from scan_repo import is_cpp_file

class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_is_cpp_file(self):
        self.assertTrue(is_cpp_file("main.cpp"))
        self.assertTrue(is_cpp_file("utils.h"))
        self.assertTrue(is_cpp_file("lib.c"))
        self.assertFalse(is_cpp_file("readme.md"))
        self.assertFalse(is_cpp_file("script.py"))

    def test_cpp_parser(self):
        file_path = os.path.join(self.test_dir, "test.cpp")
        with open(file_path, "w") as f:
            f.write('#include <iostream>\n')
            f.write('#include "myheader.h"\n')
            f.write('\n')
            f.write('class MyClass {\n')
            f.write('  int x;\n')
            f.write('};\n')
            
        metrics = parse_cpp_file(file_path)
        self.assertEqual(metrics['loc'], 5) # 6 lines total, 1 empty
        self.assertEqual(len(metrics['includes']), 2)
        self.assertIn('iostream', metrics['includes'])
        self.assertEqual(len(metrics['classes']), 1)
        self.assertEqual(metrics['classes'][0], 'MyClass')

if __name__ == '__main__':
    unittest.main()
