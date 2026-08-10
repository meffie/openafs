# This script registers the completion function for different OpenAFS
# commands. The completion function asks the command being completed for
# possible completions by calling its -completion-helper option.
#
# Source this file to register the completions.
#
#   $ source openafs_completion.zsh
#

_openafs_cmd_completion()
{
    local cmd="${words[1]}" # words[1] is the command name
    # CURRENT is 1-based in zsh, but -completion-helper expects 0-based
    local curr_word=$((CURRENT-1))

    local cmd_list=$("$cmd" -completion-helper -- "$curr_word" "${words[@]}")
    compadd -- ${=cmd_list}
}

# Register command completions.
compdef _openafs_cmd_completion bos
compdef _openafs_cmd_completion fs
compdef _openafs_cmd_completion pts
compdef _openafs_cmd_completion vos
compdef _openafs_cmd_completion volinfo
compdef _openafs_cmd_completion volscan
compdef _openafs_cmd_completion xstat_cm_test
compdef _openafs_cmd_completion xstat_fs_test
