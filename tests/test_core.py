import unittest
from context_lens.engine import Skeletonizer

class TestSkeletonizer(unittest.TestCase):
    def test_pruning(self):
        engine = Skeletonizer()
        code = "def hello(name): return f'Hello {name}'"
        result = engine.process_file("test.py", code)
        self.assertEqual(len(result.symbols), 1)
        self.assertEqual(result.symbols[0].name, "hello")

if __name__ == '__main__':
    unittest.main()