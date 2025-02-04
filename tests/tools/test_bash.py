import os
import platform
import sys
import unittest

import libkcov
from libkcov import cobertura


class BashBase(libkcov.TestCase):
    def doTest(self, args):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/shell-main "
            + args
        )

        return cobertura.parseFile(self.outbase + "/kcov/shell-main/cobertura.xml")


class bash_coverage(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov + " " + self.outbase + "/kcov " + self.sources + "/tests/bash/shell-main"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/shell-main/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "shell-main", 3) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 4) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 13) == 0
        assert cobertura.hitsPerLine(dom, "shell-main", 26) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 30) == 5
        assert cobertura.hitsPerLine(dom, "shell-main", 34) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 38) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 5) == 1

        assert cobertura.hitsPerLine(dom, "short-test.sh", 5) == 11
        assert cobertura.hitsPerLine(dom, "shell-main", 128) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 132) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 135) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 136) == 1

        assert b"I'm echoing to stderr via some" in o


# Very limited, will expand once it's working better
class bash_coverage_debug_trap(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " --bash-method=DEBUG "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/shell-main 5"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/shell-main/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "shell-main", 3) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 4) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 22) == 1


class bash_short_file(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov + " " + self.outbase + "/kcov " + self.sources + "/tests/bash/short-test.sh"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/short-test.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "short-test.sh", 5) == 11


class bash_heredoc_backslashes(BashBase):
    def runTest(self):
        dom = self.doTest("5")

        assert cobertura.hitsPerLine(dom, "shell-main", 52) == 4
        assert cobertura.hitsPerLine(dom, "shell-main", 53) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 55) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 59) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 61) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 62) is None


class bash_heredoc_special_cases_issue_44(BashBase):
    def runTest(self):
        dom = self.doTest("")
        assert cobertura.hitsPerLine(dom, "shell-main", 77) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 83) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 88) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 93) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 109) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 118) == 1


class bash_non_empty_braces(BashBase):
    def runTest(self):
        dom = self.doTest("")
        assert cobertura.hitsPerLine(dom, "shell-main", 102) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 103) == 3


class bash_coverage_tricky(BashBase):
    def runTest(self):
        dom = self.doTest("5")
        assert cobertura.hitsPerLine(dom, "shell-main", 36) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 44) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 7) is None


class bash_honor_signal(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.sources
            + "/tests/setpgid-kill/test-script.sh "
            + self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/trap.sh",
            False,
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/trap.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "trap.sh", 5) == 1


class bash_accumulate_data(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/unitundertest.sh 1"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/unitundertest.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 6) == 1
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 16) == 0
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/unitundertest.sh 2"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/unitundertest.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 6) == 1
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 16) == 1


class bash_accumulate_changed_data(libkcov.TestCase):
    # Not sure why, but for now...
    @unittest.skipUnless(platform.machine() in ["x86_64", "i686", "i386"], "Only for x86")
    def runTest(self):
        os.system("mkdir -p /tmp/test-kcov")
        os.system("cp " + self.sources + "/tests/bash/shell-main /tmp/test-kcov")
        os.system("cp " + self.sources + "/tests/bash/other.sh /tmp/test-kcov")
        rv, o = self.do(self.kcov + " " + self.outbase + "/kcov /tmp/test-kcov/shell-main 5 9")

        dom = cobertura.parseFile(self.outbase + "/kcov/shell-main/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "shell-main", 40) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 67) == 2
        assert cobertura.hitsPerLine(dom, "other.sh", 6) == 2
        os.system("echo \"echo 'arne-anka'\" >> /tmp/test-kcov/shell-main")
        rv, o = self.do(self.kcov + " " + self.outbase + "/kcov /tmp/test-kcov/shell-main 5")

        dom = cobertura.parseFile(self.outbase + "/kcov/shell-main/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "shell-main", 40) == 0
        assert cobertura.hitsPerLine(dom, "shell-main", 67) == 0
        assert cobertura.hitsPerLine(dom, "other.sh", 6) == 3


class bash_merge_data_issue_38(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/unitundertest.sh 1"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/unitundertest.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 6) == 1
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 16) == 0
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/unitundertest.sh 2"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/unitundertest.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 6) == 1
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 16) == 1
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/unitundertest.sh all"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/unitundertest.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 36) == 1
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 30) == 1
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 33) == 1
        assert cobertura.hitsPerLine(dom, "unitundertest.sh", 36) == 1


class bash_issue_116_arithmetic_and_heredoc_issue_117_comment_within_string(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov + " " + self.outbase + "/kcov " + self.sources + "/tests/bash/shell-main"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/shell-main/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "shell-main", 142) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 149) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 151) == 1
        assert cobertura.hitsPerLine(dom, "shell-main", 152) == 1


class bash_multiline_quotes(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/multiline-alias.sh"
        )

        assert b"echo called test_alias" not in o
        dom = cobertura.parseFile(self.outbase + "/kcov/multiline-alias.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "multiline-alias.sh", 6) == 1


class bash_multiline_backslashes(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/multiline-backslash.sh"
        )

        assert b"function_name" not in o


class bash_no_executed_lines(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/no-executed-statements.sh"
        )

        assert b"echo called test_alias" not in o
        dom = cobertura.parseFile(self.outbase + "/kcov/no-executed-statements.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "no-executed-statements.sh", 4) == 0


class bash_stderr_redirection(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/redirect-stderr.sh"
        )

        assert b"kcov" not in o
        rv, o = self.do(
            self.kcov
            + " --debug-force-bash-stderr "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/redirect-stderr.sh"
        )
        assert b"kcov" not in o


class bash_dollar_var_replacement(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/dollar-var-replacements.sh"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/dollar-var-replacements.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "dollar-var-replacements.sh", 2) == 1
        assert cobertura.hitsPerLine(dom, "dollar-var-replacements.sh", 4) == 1
        assert cobertura.hitsPerLine(dom, "dollar-var-replacements.sh", 5) == 1


# Issue #152
class bash_done_eof(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov + " " + self.outbase + "/kcov " + self.sources + "/tests/bash/shell-main 5"
        )
        dom = cobertura.parseFile(self.outbase + "/kcov/shell-main/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "shell-main", 163) is None
        assert cobertura.hitsPerLine(dom, "shell-main", 169) is None


# Issue #154
class bash_eof_backtick(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov + " " + self.outbase + "/kcov " + self.sources + "/tests/bash/shell-main"
        )
        dom = cobertura.parseFile(self.outbase + "/kcov/shell-main/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "shell-main", 180) == 1


class bash_subshell(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov + " " + self.outbase + "/kcov " + self.sources + "/tests/bash/subshell.sh"
        )
        dom = cobertura.parseFile(self.outbase + "/kcov/subshell.sh/cobertura.xml")
        self.assertIsNone(cobertura.hitsPerLine(dom, "subshell.sh", 1))
        self.assertEqual(2, cobertura.hitsPerLine(dom, "subshell.sh", 4))
        self.assertEqual(0, cobertura.hitsPerLine(dom, "subshell.sh", 8))


class bash_handle_all_output(libkcov.TestCase):
    def runTest(self):
        script = "handle-all-output.sh"
        rv, o = self.do(
            self.kcov + " " + self.outbase + "/kcov " + self.sources + "/tests/bash/" + script,
            timeout=5.0,
        )
        self.assertEqual(0, rv, "kcov exited unsuccessfully")
        dom = cobertura.parseFile(self.outbase + "/kcov/" + script + "/cobertura.xml")
        self.assertIsNone(cobertura.hitsPerLine(dom, script, 1))
        self.assertEqual(1000, cobertura.hitsPerLine(dom, script, 4))


class bash_exit_status(libkcov.TestCase):
    def runTest(self):
        noKcovRv, o = self.doCmd(self.sources + "/tests/bash/shell-main 5")
        rv, o = self.do(
            self.kcov + " " + self.outbase + "/kcov " + self.sources + "/tests/bash/shell-main 5"
        )

        assert rv == noKcovRv


# Issue 180
class bash_ignore_uncovered(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " --exclude-region=CUSTOM_RANGE_START:CUSTOM_RANGE_END "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/other.sh"
        )
        dom = cobertura.parseFile(self.outbase + "/kcov/other.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "other.sh", 22) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 23) == 1

        assert cobertura.hitsPerLine(dom, "other.sh", 26) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 27) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 28) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 29) == 1

        assert cobertura.hitsPerLine(dom, "other.sh", 32) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 34) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 35) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 36) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 37) == 1

        assert cobertura.hitsPerLine(dom, "other.sh", 40) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 42) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 43) == 1

        assert cobertura.hitsPerLine(dom, "other.sh", 47) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 48) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 49) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 51) == 1

        # Rust stuff
        assert cobertura.hitsPerLine(dom, "other.sh", 54) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 55) == 1


# Issue #224
class bash_can_find_non_executed_scripts(libkcov.TestCase):
    @unittest.skipUnless(platform.machine() in ["x86_64", "i686", "i386"], "Only for x86")
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/first-dir/a.sh 5"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/a.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "a.sh", 5) == 1
        # Not executed
        assert cobertura.hitsPerLine(dom, "c.sh", 3) == 0


class bash_can_find_non_executed_scripts_manually(libkcov.TestCase):
    @unittest.skipUnless(platform.machine() in ["x86_64", "i686", "i386"], "Only for x86")
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " --bash-parse-files-in-dir="
            + self.sources
            + "/tests/bash "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/first-dir/a.sh 5"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/a.sh/cobertura.xml")
        # Not executed
        assert cobertura.hitsPerLine(dom, "c.sh", 3) == 0
        assert cobertura.hitsPerLine(dom, "other.sh", 3) == 0


class bash_can_ignore_non_executed_scripts(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " --bash-dont-parse-binary-dir "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/first-dir/a.sh 5"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/a.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "a.sh", 5) == 1
        # Not included in report
        assert cobertura.hitsPerLine(dom, "c.sh", 3) is None
        assert cobertura.hitsPerLine(dom, "other.sh", 3) is None


class bash_can_ignore_function_with_spaces(libkcov.TestCase):
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " --bash-dont-parse-binary-dir "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/function-with-spaces.sh"
        )

        dom = cobertura.parseFile(self.outbase + "/kcov/function-with-spaces.sh/cobertura.xml")
        assert cobertura.hitsPerLine(dom, "function-with-spaces.sh", 5) is None
        assert cobertura.hitsPerLine(dom, "function-with-spaces.sh", 6) == 1
        assert cobertura.hitsPerLine(dom, "function-with-spaces.sh", 9) is None
        assert cobertura.hitsPerLine(dom, "function-with-spaces.sh", 10) is None
        assert cobertura.hitsPerLine(dom, "function-with-spaces.sh", 11) == 1


class bash_drain_stdout_without_return(libkcov.TestCase):
    @unittest.skipUnless(platform.machine() in ["x86_64", "i686", "i386"], "Only for x86")
    @unittest.skipIf(sys.platform.startswith("darwin"), "Not for OSX")
    def runTest(self):
        rv, o = self.do(
            self.kcov
            + " "
            + self.outbase
            + "/kcov "
            + self.sources
            + "/tests/bash/long-output-without-return.sh",
            timeout=5.0,
        )
        self.assertEqual(0, rv, "kcov exited unsuccessfully")
        dom = cobertura.parseFile(
            self.outbase + "/kcov/long-output-without-return.sh/cobertura.xml"
        )
        self.assertIsNone(cobertura.hitsPerLine(dom, "long-output-without-return.sh", 1))
        self.assertEqual(32768, cobertura.hitsPerLine(dom, "long-output-without-return.sh", 4))
