import unittest

def test_suite():
    return unittest.TestLoader().loadTestsFromNames(["test_bot", "test_cmd", "test_context"])

if __name__ == "__main__":
    # import sys
    # import os
    # sys.path.insert(0, os.path.abspath("."))
    unittest.main(defaultTest='test_suite')