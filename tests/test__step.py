import  platform, gossip
if platform.python_version() < "2.7":
    import unittest2 as unittest
else:
    import unittest
from logbook.compat import LoggingHandler
from slash_step import STEP

class StepTest(unittest.TestCase):
    def setUp(self):
        super(StepTest, self).setUp()
        self._handler = LoggingHandler()
        self._handler.push_application()
        self.actions = {'start':False, 'error':False, 'end':False, 'success':False}
        @gossip.register('slash.step_start', token="step")
        def step_start():
            self.actions['start'] = True
        @gossip.register('slash.step_end', token="step")
        def step_end():
            self.actions['end'] = True
        @gossip.register('slash.step_success', token="step")
        def step_success():
            self.actions['success'] = True
            self._verify(end=False)
        @gossip.register('slash.step_error', token="step")
        def step_error():
            self.actions['error'] = True
            self._verify(success=False, end=False, error=True)
    def tearDown(self):
        self._handler.pop_application()
        gossip.unregister_token(token="step")
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
    def test_step_creation_with_arguments(self):
        step = STEP("Message with args and kwargs", "args", kwargs='kwargs')
        self.assertEquals(step.message, "Message with args and kwargs")
    def test_step_creation_with_curly_brackets_without_arguments(self):
        message = "My message with {curly brackets}"
        step = STEP(message)
        self.assertEquals(step.message, message)
