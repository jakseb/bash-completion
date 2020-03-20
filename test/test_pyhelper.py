import subprocess

DEFAULT_INTERP = "python"
DEFAULT_NEW_HELPER = "helpers/python"
DEFAULT_OLD_HELPER = "/usr/share/bash-completion/helpers/python"


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
    if comp_old != comp_new:
        if not comp_old:
            return "fail null"
        else:
            return "fail"
    else:
        return "ok"


if __name__ == "__main__":
    import sys

    interp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INTERP
    old_helper = DEFAULT_OLD_HELPER
    new_helper = DEFAULT_NEW_HELPER
    for pkg, result in compare_all_completions(interp, old_helper, new_helper):
        print(pkg or "<toplevel>", result)
