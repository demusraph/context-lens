import unittest
from context_lens.engine import Skeletonizer

class TestClassDefinitions(unittest.TestCase):
    def setUp(self):
        self.engine = Skeletonizer(preserve_docstrings=True)

    def test_036_simple_class(self):
        code = "class MyClass: pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].name, "MyClass")
        self.assertEqual(res.symbols[0].type, "ClassDef")

    def test_037_class_with_base(self):
        code = "class Child(Base): pass"
        res = self.engine.process_file("a.py", code)
        self.assertIn("Base", res.symbols[0].signature)

    def test_038_class_with_multiple_bases(self):
        code = "class Multi(A, B, C): pass"
        res = self.engine.process_file("a.py", code)
        self.assertIn("A, B, C", res.symbols[0].signature)

    def test_039_class_with_docstring(self):
        code = '''class DocClass:
    """Class docstring."""
    pass'''
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].docstring, "Class docstring.")

    def test_040_class_with_method(self):
        code = "class Service:\n    def execute(self): return 1"
        out = self.engine.skeletonize(code)
        self.assertIn("class Service:", out)
        self.assertIn("def execute(self):", out)
        self.assertNotIn("return 1", out)

    def test_041_class_with_init(self):
        code = "class Person:\n    def __init__(self, name: str):\n        self.name = name"
        out = self.engine.skeletonize(code)
        self.assertNotIn("self.name = name", out)

    def test_042_class_with_classmethod(self):
        code = "class Factory:\n    @classmethod\n    def create(cls): return cls()"
        out = self.engine.skeletonize(code)
        self.assertIn("def create(cls):", out)
        self.assertNotIn("return cls()", out)

    def test_043_class_with_staticmethod(self):
        code = "class Math:\n    @staticmethod\n    def add(a, b): return a + b"
        out = self.engine.skeletonize(code)
        self.assertIn("def add(a, b):", out)
        self.assertNotIn("return a + b", out)

    def test_044_class_with_property(self):
        code = "class Circle:\n    @property\n    def radius(self): return self._r"
        out = self.engine.skeletonize(code)
        self.assertIn("def radius(self):", out)
        self.assertNotIn("self._r", out)

    def test_045_class_with_property_setter(self):
        code = "class Circle:\n    @radius.setter\n    def radius(self, val): self._r = val"
        out = self.engine.skeletonize(code)
        self.assertIn("def radius(self, val):", out)

    def test_046_nested_classes(self):
        code = "class Outer:\n    class Inner: pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].name, "Outer")

    def test_047_generic_class_inheritance(self):
        code = "class TypedList(Generic[T]): pass"
        res = self.engine.process_file("a.py", code)
        self.assertIn("Generic[T]", res.symbols[0].signature)

    def test_048_dataclass_decorator(self):
        code = "@dataclass\nclass User: name: str"
        out = self.engine.skeletonize(code)
        self.assertIn("class User:", out)

    def test_049_pydantic_base_model(self):
        code = "class Schema(BaseModel):\n    id: int\n    def validate(self): pass"
        out = self.engine.skeletonize(code)
        self.assertIn("class Schema(BaseModel):", out)

    def test_050_multiple_classes_in_file(self):
        code = "class A: pass\nclass B: pass\nclass C: pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(len(res.symbols), 3)

    def test_051_abstract_base_class(self):
        code = "class Abs(ABC):\n    @abstractmethod\n    def run(self): pass"
        out = self.engine.skeletonize(code)
        self.assertIn("class Abs(ABC):", out)

    def test_052_dunder_repr_method(self):
        code = "class Obj:\n    def __repr__(self): return '<Obj>'"
        out = self.engine.skeletonize(code)
        self.assertNotIn("'<Obj>'", out)

    def test_053_dunder_str_method(self):
        code = "class Obj:\n    def __str__(self): return 'Obj'"
        out = self.engine.skeletonize(code)
        self.assertNotIn("'Obj'", out)

    def test_054_dunder_eq_method(self):
        code = "class Obj:\n    def __eq__(self, other): return True"
        out = self.engine.skeletonize(code)
        self.assertNotIn("return True", out)

    def test_055_dunder_hash_method(self):
        code = "class Obj:\n    def __hash__(self): return 42"
        out = self.engine.skeletonize(code)
        self.assertNotIn("return 42", out)

    def test_056_dunder_len_method(self):
        code = "class Container:\n    def __len__(self): return 10"
        out = self.engine.skeletonize(code)
        self.assertNotIn("return 10", out)

    def test_057_dunder_getitem_method(self):
        code = "class Container:\n    def __getitem__(self, idx): return idx"
        out = self.engine.skeletonize(code)
        self.assertNotIn("return idx", out)

    def test_058_dunder_iter_method(self):
        code = "class Seq:\n    def __iter__(self): return iter([])"
        out = self.engine.skeletonize(code)
        self.assertNotIn("iter([])", out)

    def test_059_dunder_next_method(self):
        code = "class Iterator:\n    def __next__(self): raise StopIteration"
        out = self.engine.skeletonize(code)
        self.assertNotIn("StopIteration", out)

    def test_060_context_manager_enter_exit(self):
        code = "class CM:\n    def __enter__(self): return self\n    def __exit__(self, *args): pass"
        out = self.engine.skeletonize(code)
        self.assertIn("def __enter__(self):", out)
        self.assertIn("def __exit__(self, *args):", out)

    def test_061_async_context_manager(self):
        code = "class ACM:\n    async def __aenter__(self): return self\n    async def __aexit__(self, *args): pass"
        out = self.engine.skeletonize(code)
        self.assertIn("async def __aenter__(self):", out)

    def test_062_async_iterator(self):
        code = "class AIter:\n    async def __anext__(self): return 1"
        out = self.engine.skeletonize(code)
        self.assertIn("async def __anext__(self):", out)

    def test_063_dunder_call_callable_class(self):
        code = "class CallableObj:\n    def __call__(self, x): return x * 2"
        out = self.engine.skeletonize(code)
        self.assertNotIn("return x * 2", out)

    def test_064_class_with_metaclass(self):
        code = "class MetaUser(metaclass=Singleton): pass"
        res = self.engine.process_file("a.py", code)
        self.assertEqual(res.symbols[0].name, "MetaUser")

    def test_065_class_with_slots(self):
        code = "class Point:\n    __slots__ = ('x', 'y')\n    def dist(self): return 0"
        out = self.engine.skeletonize(code)
        self.assertIn("class Point:", out)

    def test_066_class_docstring_stripping_option(self):
        engine = Skeletonizer(preserve_docstrings=False)
        code = 'class C:\n    """Remove class doc."""\n    pass'
        res = engine.process_file("a.py", code)
        self.assertIsNone(res.symbols[0].docstring)

    def test_067_class_attribute_preservation(self):
        code = "class Config:\n    TIMEOUT = 30\n    DEBUG = True"
        out = self.engine.skeletonize(code)
        self.assertIn("TIMEOUT = 30", out)

    def test_068_enum_class(self):
        code = "class Color(Enum):\n    RED = 1\n    BLUE = 2"
        out = self.engine.skeletonize(code)
        self.assertIn("class Color(Enum):", out)

    def test_069_exception_subclass(self):
        code = "class CustomError(Exception):\n    def __init__(self, msg): super().__init__(msg)"
        out = self.engine.skeletonize(code)
        self.assertIn("class CustomError(Exception):", out)

    def test_070_subclass_super_call(self):
        code = "class Derived(Base):\n    def action(self): return super().action()"
        out = self.engine.skeletonize(code)
        self.assertNotIn("super().action()", out)

if __name__ == '__main__':
    unittest.main()
