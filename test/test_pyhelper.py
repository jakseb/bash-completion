#!/usr/bin/env python3

import argparse
import subprocess

DEFAULT_INTERP = "python"
DEFAULT_NEW_HELPER = "helpers/python"
DEFAULT_OLD_HELPER = "/usr/share/bash-completion/helpers/python"


class CompletionDiff:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def equal(self):
        return len(self.left) == len(self.right) == 0


def completions(interp, helper, prefix):
    return set(filtercomp(raw_completions(interp, helper, prefix), prefix))


def raw_completions(interp, helper, prefix):
    return subprocess.run(
        [interp, helper, prefix],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    ).stdout.splitlines()


def filtercomp(s, prefix):
    return (c for c in s if c.startswith(prefix))


def compare_all_completions(interp, old_helper, new_helper):
    comp_old = completions(interp, old_helper, "")
    comp_new = completions(interp, new_helper, "")
    result = compare_completions(comp_old, comp_new)
    yield None, result

    rcomp_old = list(raw_completions(interp, old_helper, "."))
    for pkg in rcomp_old:
        prefix = pkg + "."
        comp_old = set(filtercomp(rcomp_old, prefix))
        comp_new = completions(interp, new_helper, prefix)
        result = compare_completions(comp_old, comp_new)
        yield pkg, result


def compare_completions(comp_old, comp_new):
    return CompletionDiff(comp_old - comp_new, comp_new - comp_old)


def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--old",
        help="old/reference helper location",
        dest="old_helper",
        default=DEFAULT_OLD_HELPER,
    )
    parser.add_argument(
        "-n",
        "--new",
        help="new/tested helper location",
        dest="new_helper",
        default=DEFAULT_NEW_HELPER,
    )
    parser.add_argument(
        "interp",
        help="Python interpreter to run helpers under",
        nargs="?",
        default=DEFAULT_INTERP,
    )
    return parser.parse_args()


if __name__ == "__main__":

    opts = parse_cmdline()
    for pkg, diff in compare_all_completions(
        opts.interp, opts.old_helper, opts.new_helper
    ):
        pkg = pkg or "<toplevel>"
        if diff.equal:
            result = "ok"
        else:
            result = "fail {} {}".format(len(diff.left), len(diff.right))
        print(pkg, result)
        if not diff.equal:
            for name in diff.left:
                print("-", name)
            for name in diff.right:
                print("+", name)
