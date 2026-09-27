import unittest
from context_lens.engine import Skeletonizer

class TestFunctionSignatures(unittest.TestCase):
    def setUp(self):
        self.engine = Skeletonizer(preserve_docstrings=True)

    def test_001_single_arg(self):
        res = self.engine.process_file("a.py", "def fn(a): pass")
        self.assertEqual(len(res.symbols), 1)
        self.assertEqual(res.symbols[0].name, "fn")

    def test_002_multi_args(self):
        res = self.engine.process_file("a.py", "def fn(a, b, c): return a+b+c")
        self.assertIn("a, b, c", res.symbols[0].signature)

    def test_003_no_args(self):
        res = self.engine.process_file("a.py", "def fn(): return 42")
        self.assertEqual(res.symbols[0].signature, "def fn()")

    def test_004_async_function(self):
        res = self.engine.process_file("a.py", "async def fetch(): pass")
        self.assertEqual(res.symbols[0].type, "AsyncFunctionDef")
        self.assertIn("async def fetch", res.symbols[0].signature)

    def test_005_with_docstring(self):
        code = '''def compute():
    """Computes value."""
    return 100'''
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].docstring, "Computes value.")

    def test_006_skeletonize_strips_body(self):
        code = "def complex_calc():\n    x = 10\n    y = 20\n    return x * y"
        out = self.engine.skeletonize(code)
        self.assertNotIn("x = 10", out)
        self.assertIn("def complex_calc():", out)

    def test_007_skeletonize_keeps_docstring(self):
        code = 'def test():\n    """Docstring here."""\n    x = 1\n    return x'
        out = self.engine.skeletonize(code)
        self.assertIn("Docstring here.", out)
        self.assertNotIn("x = 1", out)

    def test_008_docstring_stripping_option(self):
        engine = Skeletonizer(preserve_docstrings=False)
        code = 'def test():\n    """Remove me."""\n    return 1'
        out = engine.skeletonize(code)
        self.assertNotIn("Remove me.", out)

    def test_009_multi_function_file(self):
        code = "def f1(): pass\ndef f2(): pass\ndef f3(): pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(len(res.symbols), 3)

    def test_010_type_annotated_args(self):
        code = "def greet(name: str) -> str: return f'Hi {name}'"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].name, "greet")

    def test_011_default_arguments(self):
        code = "def connect(host='localhost', port=8080): pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].name, "connect")

    def test_012_token_reduction_calculation(self):
        code = "def long_func():\n" + "\n".join(f"    a_{i} = {i}" for i in range(50)) + "\n    return a_0"
        res = self.engine.process_file("a.py", code)
        self.assertLess(res.pruned_tokens, res.total_tokens)

    def test_013_preserve_decorator_structure(self):
        code = "@property\ndef prop(): return 1"
        out = self.engine.skeletonize(code)
        self.assertIn("def prop():", out)

    def test_014_nested_functions(self):
        code = "def outer():\n    def inner(): pass\n    return inner"
        out = self.engine.skeletonize(code)
        self.assertIn("def outer():", out)

    def test_015_generator_function(self):
        code = "def gen():\n    yield 1\n    yield 2"
        out = self.engine.skeletonize(code)
        self.assertNotIn("yield 1", out)

    def test_016_variadic_args(self):
        code = "def var(*args, **kwargs): pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].name, "var")

    def test_017_kwonly_args(self):
        code = "def kw(*, key=True): pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].name, "kw")

    def test_018_posonly_args(self):
        code = "def pos(a, /, b): pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].name, "pos")

    def test_019_multiple_async_functions(self):
        code = "async def a1(): pass\nasync def a2(): pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(len(res.symbols), 2)
        self.assertTrue(all(s.type == "AsyncFunctionDef" for s in res.symbols))

    def test_020_docstring_multiline(self):
        code = '''def multi():
    """
    Line 1
    Line 2
    """
    return True'''
        res = self.engine.process_file("a.py", code)
        self.assertIn("Line 1", res.symbols[0].docstring)

    def test_021_return_constant(self):
        code = "def ret(): return None"
        out = self.engine.skeletonize(code)
        self.assertNotIn("return None", out)

    def test_022_try_except_body(self):
        code = "def err():\n    try:\n        1/0\n    except Exception:\n        pass"
        out = self.engine.skeletonize(code)
        self.assertNotIn("1/0", out)

    def test_023_while_loop_body(self):
        code = "def loop():\n    while True:\n        break"
        out = self.engine.skeletonize(code)
        self.assertNotIn("while True", out)

    def test_024_for_loop_body(self):
        code = "def iterate():\n    for x in range(10):\n        print(x)"
        out = self.engine.skeletonize(code)
        self.assertNotIn("for x in range", out)

    def test_025_with_statement_body(self):
        code = "def file_op():\n    with open('f') as f:\n        return f.read()"
        out = self.engine.skeletonize(code)
        self.assertNotIn("open('f')", out)

    def test_026_match_case_body(self):
        code = "def matcher(val):\n    match val:\n        case 1: return 'one'\n        case _: return 'other'"
        out = self.engine.skeletonize(code)
        self.assertNotIn("case 1", out)

    def test_027_raise_exception_body(self):
        code = "def fail(): raise ValueError('boom')"
        out = self.engine.skeletonize(code)
        self.assertNotIn("ValueError", out)

    def test_028_assert_statement_body(self):
        code = "def check(): assert True, 'ok'"
        out = self.engine.skeletonize(code)
        self.assertNotIn("assert True", out)

    def test_029_lambda_expression_inside(self):
        code = "def sort_fn(): f = lambda x: x[0]; return f"
        out = self.engine.skeletonize(code)
        self.assertNotIn("lambda x", out)

    def test_030_list_comprehension_inside(self):
        code = "def comp(): return [x*2 for x in range(10)]"
        out = self.engine.skeletonize(code)
        self.assertNotIn("for x in range(10)", out)

    def test_031_dict_comprehension_inside(self):
        code = "def dcomp(): return {k: v for k, v in [(1,2)]}"
        out = self.engine.skeletonize(code)
        self.assertNotIn("for k, v in", out)

    def test_032_set_comprehension_inside(self):
        code = "def scomp(): return {x for x in (1,2,3)}"
        out = self.engine.skeletonize(code)
        self.assertNotIn("x for x in", out)

    def test_033_walrus_operator_inside(self):
        code = "def wal():\n    if (n := len('abc')) > 2:\n        return n"
        out = self.engine.skeletonize(code)
        self.assertNotIn("len('abc')", out)

    def test_034_consecutive_return_statements(self):
        code = "def guards(x):\n    if x < 0: return -1\n    if x == 0: return 0\n    return 1"
        out = self.engine.skeletonize(code)
        self.assertNotIn("return -1", out)

    def test_035_empty_pass_function(self):
        code = "def dummy(): pass"
        out = self.engine.skeletonize(code)
        self.assertIn("def dummy():", out)

if __name__ == '__main__':
    unittest.main()