# This script registers the completion function for different OpenAFS
# commands. The completion function asks the command being completed for
# possible completions by calling its -completion-helper option.
#
# Source this file to register the completions.
#
#   $ source openafs_completion.bash
#

_OPENAFS_COMMANDS=(
    afsd
    afsd.fuse
    afsio
    akeyconvert
    bos
    butc
    cmdebug
    dafssync-debug
    fs
    fssync-debug
    fstrace
    klog.krb5
    livesys
    prdb_check
    pts
    pt_util
    read_tape
    restorevol
    rxdebug
    rxstat_clear_peer
    rxstat_clear_process
    rxstat_disable_peer
    rxstat_disable_process
    rxstat_enable_peer
    rxstat_enable_process
    rxstat_get_peer
    rxstat_get_process
    rxstat_get_version
    rxstat_query_peer
    rxstat_query_process
    salvsync-debug
    scout
    sys
    tokens
    udebug
    unlog
    vldb_check
    vldb_convert
    voldump
    volinfo
    volscan
    vos
    xstat_cm_test
    xstat_fs_test
)

_openafs_cmd_completion()
{
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local cmd="$1" # $1 is the command name

    local cmd_list=$("$cmd" -completion-helper -- "$COMP_CWORD" "${COMP_WORDS[@]}")
    COMPREPLY=( $(compgen -W "$cmd_list" -- "$cur") )
}

# Register command completions.
for cmd in "${_OPENAFS_COMMANDS[@]}"; do
    complete -F _openafs_cmd_completion $cmd
done
