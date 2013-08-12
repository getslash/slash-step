import  platform
if platform.python_version() < "2.7":
    import unittest2 as unittest
else:
    import unittest
from logbook.compat import LoggingHandler
from slash_step import STEP
from slash_step import hooks

class StepTest(unittest.TestCase):
    def setUp(self):
        super(StepTest, self).setUp()
        self._handler = LoggingHandler()
        self._handler.push_application()
        self.actions = {'start':False, 'error':False, 'end':False, 'success':False}
        @hooks.step_start.register
        def step_start():
            self.actions['start'] = True
        @hooks.step_end.register
        def step_end():
            self.actions['end'] = True
        @hooks.step_success.register
        def step_success():
            self.actions['success'] = True
            self._verify(end=False)
        @hooks.step_error.register
        def step_error():
            self.actions['error'] = True
            self._verify(success=False, end=False, error=True)
    def tearDown(self):
        self._handler.pop_application()
        hooks.step_start.unregister_by_identifier(None)
        hooks.step_end.unregister_by_identifier(None)
        hooks.step_success.unregister_by_identifier(None)
        hooks.step_error.unregister_by_identifier(None)
        super(StepTest, self).tearDown()
    def test_step_entry(self):
        msg = "Some step message"
        with STEP(msg) as step:
            self.assertIsInstance(step, STEP)
            self.assertEquals(str(step), msg)
            self.assertIn(msg, repr(step))
    def test_step_success(self):
        with STEP("This will succeed"):
            self._verify(success=False, end=False)
        self._verify()
    def test_step_error(self):
        with self.assertRaises(AssertionError):
            with STEP("This will fail"):
                assert 1 == 0
        self._verify(success=False, error=True)
    def _verify(self, start=True, success=True, end=True, error=False):
        self.assertEquals(start, self.actions['start'])
        self.assertEquals(end, self.actions['end'])
        self.assertEquals(success, self.actions['success'])
        self.assertEquals(error, self.actions['error'])
