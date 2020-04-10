oksameln() {
    awk '
    function clearok() {
        if (F2 == "ok")
            printf "%s", "\r\033[A\033[K"
    }

    { clearok() }
    1;
    { F2 = $2 }
    END { clearok() }
    '
}

readdate() {
    read "${1:?}" "${2:?}" <<<"$(date +'%-s %-N')"
}

fmtime() {
    ( :
    s2="${1:?}" ns2="${2:-0}"
    h="$((s2 / 3600))"
    m="$((s2 % 3600 / 60))"
    s="$((s2 % 60))"
    ms="$((ns2 / 1000000))"
    [ $h = 0 ] && h=
    [ $m = 0 ] && m=
    printf '%s.%03ds\n' "${h:+${h}h}${m:+${m}m}${s}" "${ms}"
    : )
}

difftime() {
    ( :
    s1="${1:?}" s0="${2:?}" ns1="${3:?}" ns0="${4:?}"
    if [ "$ns1" -ge "$ns0" ]
    then
        echo $((s1-s0)) $((ns1-ns0))
    else
        echo $((s1-s0-1)) $((ns1-ns0+1000000000))
    fi
    : )
}

mkpyvenv() {
    ( :
    prog="${1:?}" || return 1
    dir="/tmp/venv-$prog"
    [ -d "$dir" ] && return
    ver="$("$prog" -c 'import sys; print(sys.version_info[0])')"
    if [ "$ver" = 3 ]
    then
        mod=venv
    else
        mod=virtualenv
    fi
    "$prog" -m "$mod" "$dir"
    : )
}

mkpyhdiff() {
    ( :
    old="${1:?}" new="${2:?}" || return 1
    pythons="${pythons:-$(echo {venv-,}{python{2,3},pypy3})}"
    [ -f "pyh/$old" ] || return 1
    [ -f "pyh/$new" ] || return 1
    outd="$(mktemp -d pyhd.tmp.XXXXXX)"
    for py in $pythons
    do
        if [[ $py != venv-* ]]
        then
            key="$py"
            prog="$py"
        else
            py_="${py/#venv-}"
            key="v$py_"
            prog="/tmp/venv-$py_/bin/python"
            mkpyvenv "$py_"
        fi
        echo "___ $py ___"
        outfile="$outd/$old-$new-$key.diff"
        readdate s0 ns0
        python -u test/test_pyhelper.py -o "pyh/$old" -n "pyh/$new" "$prog" |
            tee "$outfile.part" |
            oksameln
        readdate s1 ns1
        echo "elapsed: $(fmtime $(difftime "$s1" "$s0" "$ns1" "$ns0"))"
        mv "$outfile.part" "$outfile"
    done
    mv "$outd"/* pyhd/
    rmdir -- "$outd"
    : )
}
