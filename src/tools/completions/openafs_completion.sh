# This script registers the same completion function for different OpenAFS
# commands. The completion function asks the command being completed for
# possible completions by calling its -completion-helper option.
#
# For manual testing, source this file once for each command name:
#   $ source src/tools/completions/openafs_completion.sh fs
#   $ source src/tools/completions/openafs_completion.sh vos

_openafs_cmd_completion()
{
	# COMP_WORDS and COMP_CWORD are set by Bash before calling this function.
	# COMP_CWORD is the index of the word being completed.
	# COMP_WORDS is the array of typed words.
	local cur="${COMP_WORDS[COMP_CWORD]}"
	# $1 is the command name, passed by Bash when completion is triggered.
    local cmd="$1"

	local cmd_list=$("$cmd" -completion-helper -- "$COMP_CWORD" "${COMP_WORDS[@]}" 2>/dev/null)
	# COMPREPLY is the list of completion candidates that Bash displays.
	COMPREPLY=( $(compgen -W "$cmd_list" -- "$cur") )
}

# $1 here is the command name passed when sourcing this file.
complete -F _openafs_cmd_completion "$1"
