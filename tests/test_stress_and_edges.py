import unittest
from context_lens.engine import Skeletonizer

class TestStressAndEdgeCases(unittest.TestCase):
    def setUp(self):
        self.engine = Skeletonizer(preserve_docstrings=True)

    def test_071_empty_string(self):
        res = self.engine.process_file("empty.py", "")
        self.assertEqual(len(res.symbols), 0)
        self.assertEqual(res.total_tokens, 0)

    def test_072_whitespace_only(self):
        res = self.engine.process_file("ws.py", "   \n\t\n   ")
        self.assertEqual(len(res.symbols), 0)

    def test_073_comments_only(self):
        code = "# Just comments\n# Another comment\n"
        res = self.engine.process_file("comments.py", code)
        self.assertEqual(len(res.symbols), 0)

    def test_074_syntax_error_resilience(self):
        code = "def broken(::"
        res = self.engine.process_file("broken.py", code)
        self.assertEqual(len(res.symbols), 0)

    def test_075_unicode_function_names(self):
        code = "def calculate_π(r): return 3.14 * r"
        res = self.engine.process_file("unicode.py", code)
        self.assertEqual(res.symbols[0].name, "calculate_π")

    def test_076_unicode_docstrings(self):
        code = 'def test():\n    """こんにちは世界 — Hello World"""\n    pass'
        res = self.engine.process_file("u_doc.py", code)
        self.assertIn("こんにちは世界", res.symbols[0].docstring)

    def test_077_deeply_nested_blocks(self):
        code = """def deep():
    if True:
        for i in range(1):
            while False:
                try:
                    return 42
                finally:
                    pass"""
        out = self.engine.skeletonize(code)
        self.assertNotIn("finally", out)

    def test_078_large_synthetic_file_100_functions(self):
        funcs = [f"def fn_{i}(x: int) -> int:\n    return x + {i}" for i in range(100)]
        code = "\n\n".join(funcs)
        res = self.engine.process_file("large.py", code)
        self.assertEqual(len(res.symbols), 100)

    def test_079_large_file_pruning_performance(self):
        funcs = [f"def fn_{i}(x: int) -> int:\n    y = x * 2\n    return y + {i}" for i in range(50)]
        code = "\n\n".join(funcs)
        out = self.engine.skeletonize(code)
        self.assertEqual(out.count("..."), 50)

    def test_080_crlf_preservation_support(self):
        code = "def crlf_func():\r\n    x = 10\r\n    return x\r\n"
        out = self.engine.skeletonize(code)
        self.assertIn("def crlf_func():", out)

    def test_081_mixed_tabs_and_spaces(self):
        code = "def mixed():\n    x = 1\n    return x"
        res = self.engine.process_file("mix.py", code)
        self.assertEqual(res.symbols[0].name, "mixed")

    def test_082_global_variables_unaffected(self):
        code = "GLOBAL_CONST = 100\ndef fn(): pass"
        out = self.engine.skeletonize(code)
        self.assertIn("GLOBAL_CONST = 100", out)

    def test_083_import_statements_unaffected(self):
        code = "import os\nfrom pathlib import Path\ndef fn(): pass"
        out = self.engine.skeletonize(code)
        self.assertIn("import os", out)
        self.assertIn("from pathlib import Path", out)

    def test_084_multiple_decorators(self):
        code = "@dec1\n@dec2(opt=True)\ndef decorated(): pass"
        out = self.engine.skeletonize(code)
        self.assertIn("@dec1", out)
        self.assertIn("@dec2(opt=True)", out)

    def test_085_chained_method_calls_in_body(self):
        code = "def pipeline(): return df.filter().groupby().sum()"
        out = self.engine.skeletonize(code)
        self.assertNotIn("groupby()", out)

    def test_086_multiline_arguments(self):
        code = """def long_args(
    param1: str,
    param2: int,
    param3: float
):
    return True"""
        res = self.engine.process_file("args.py", code)
        self.assertEqual(res.symbols[0].name, "long_args")

    def test_087_return_type_complex_union(self):
        code = "def complex_ret() -> Union[int, List[str], Dict[str, Any]]: pass"
        res = self.engine.process_file("ret.py", code)
        self.assertEqual(res.symbols[0].name, "complex_ret")

    def test_088_bitwise_operations_in_body(self):
        code = "def bitwise(a, b): return (a ^ b) | (a & b) << 2"
        out = self.engine.skeletonize(code)
        self.assertNotIn("a ^ b", out)

    def test_089_nested_try_except_finally(self):
        code = "def safe():\n    try:\n        pass\n    except:\n        try:\n            pass\n        finally:\n            pass"
        out = self.engine.skeletonize(code)
        self.assertNotIn("finally", out)

    def test_090_f_strings_in_body(self):
        code = "def format_msg(user): return f'Welcome, {user.upper()}!'"
        out = self.engine.skeletonize(code)
        self.assertNotIn("Welcome,", out)

    def test_091_regex_raw_strings_in_body(self):
        code = r"def matcher(s): return re.match(r'^\d{3}-\d{2}-\d{4}$', s)"
        out = self.engine.skeletonize(code)
        self.assertNotIn(r"^\d{3}", out)

    def test_092_assert_statements_stripped(self):
        code = "def strict(x): assert x > 0, 'Must be positive'; return x"
        out = self.engine.skeletonize(code)
        self.assertNotIn("Must be positive", out)

    def test_093_del_statement_stripped(self):
        code = "def clean(d): del d['key']; return d"
        out = self.engine.skeletonize(code)
        self.assertNotIn("del d", out)

    def test_094_pass_only_class_body(self):
        code = "class Marker: pass"
        out = self.engine.skeletonize(code)
        self.assertIn("class Marker:", out)

    def test_095_empty_class_body_with_doc(self):
        code = 'class Marker:\n    """Marker doc."""'
        res = self.engine.process_file("mark.py", code)
        self.assertEqual(res.symbols[0].docstring, "Marker doc.")

    def test_096_multiple_docstrings_in_file(self):
        code = '"""Module doc."""\ndef f():\n    """Fn doc."""\n    pass'
        res = self.engine.process_file("m.py", code)
        self.assertEqual(res.symbols[0].docstring, "Fn doc.")

    def test_097_token_reduction_ratio_positive(self):
        code = "def verbose():\n" + "\n".join(f"    var_{i} = 'some long string value {i}'" for i in range(30)) + "\n    return var_0"
        res = self.engine.process_file("v.py", code)
        self.assertGreater(res.total_tokens, res.pruned_tokens)

    def test_098_static_analysis_preserves_class_signatures(self):
        code = "class Router(BaseRouter, ABC):\n    pass"
        res = self.engine.process_file("r.py", code)
        self.assertIn("BaseRouter, ABC", res.symbols[0].signature)

    def test_099_async_generator(self):
        code = "async def stream():\n    for i in range(10):\n        yield i"
        out = self.engine.skeletonize(code)
        self.assertIn("async def stream():", out)

    def test_100_special_characters_in_strings(self):
        code = "def special():\n    s = 'Quotes \" and \\' and \\n and \\t'\n    return s"
        out = self.engine.skeletonize(code)
        self.assertNotIn("Quotes", out)

    def test_101_multiline_docstring_indentation(self):
        code = '''def indented_doc():
        """
        Deeply indented
        docstring line
        """
        return 1'''
        res = self.engine.process_file("ind.py", code)
        self.assertIn("Deeply indented", res.symbols[0].docstring)

    def test_102_class_with_inner_functions(self):
        code = "class Container:\n    def method(self):\n        def helper(): return 2\n        return helper()"
        out = self.engine.skeletonize(code)
        self.assertNotIn("helper()", out)

    def test_103_complex_dataclass_fields(self):
        code = "@dataclass\nclass Config:\n    host: str = '0.0.0.0'\n    port: int = 8080\n    def url(self): return f'{self.host}:{self.port}'"
        out = self.engine.skeletonize(code)
        self.assertIn("class Config:", out)

    def test_104_all_exported_symbols_recorded(self):
        code = "__all__ = ['A', 'b']\nclass A: pass\ndef b(): pass"
        res = self.engine.process_file("exp.py", code)
        names = [s.name for s in res.symbols]
        self.assertIn("A", names)
        self.assertIn("b", names)

    def test_105_stress_mixed_constructs_end_to_end(self):
        code = '''
import os
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """Abstract processor."""
    @abstractmethod
    def process(self, data: str) -> bool:
        """Process implementation."""
        pass

class RealProcessor(BaseProcessor):
    def process(self, data: str) -> bool:
        x = data.strip().lower()
        if len(x) > 10:
            return True
        return False

async def orchestrate():
    """Async main orchestrator."""
    p = RealProcessor()
    return p.process("test")
'''
        res = self.engine.process_file("stress.py", code)
        self.assertEqual(len(res.symbols), 3)
        out = self.engine.skeletonize(code)
        self.assertIn("class BaseProcessor(ABC):", out)
        self.assertIn("class RealProcessor(BaseProcessor):", out)
        self.assertIn("async def orchestrate():", out)
        self.assertNotIn("x = data.strip().lower()", out)

if __name__ == '__main__':
    unittest.main()
