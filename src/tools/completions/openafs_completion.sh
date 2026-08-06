# This script registers the completion function for different OpenAFS
# commands. The completion function asks the command being completed for
# possible completions by calling its -completion-helper option.
#
# Source this file to register the completions.
#
#   $ source openafs_completion.sh
#

_openafs_cmd_completion()
{
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local cmd="$1" # $1 is the command name

    local cmd_list=$("$cmd" -completion-helper -- "$COMP_CWORD" "${COMP_WORDS[@]}")
    COMPREPLY=( $(compgen -W "$cmd_list" -- "$cur") )
}

# Register command completions.
complete -F _openafs_cmd_completion bos
complete -F _openafs_cmd_completion fs
complete -F _openafs_cmd_completion pts
complete -F _openafs_cmd_completion vos
complete -F _openafs_cmd_completion volinfo
complete -F _openafs_cmd_completion volscan
