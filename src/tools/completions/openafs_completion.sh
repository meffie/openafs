# Bash completion function that calls the OpenAFS command with -completion-helper, the number of words and the
# array of words to get the list of possible completions based on the current command line context, then uses
# compgen to filter the list based on the current word.

_openafs_cmd_completion()
{
	local cur="${COMP_WORDS[COMP_CWORD]}"
    local cmd="$1"

	local cmd_list=$("$cmd" -completion-helper -- "$COMP_CWORD" "${COMP_WORDS[@]}" 2>/dev/null)
	COMPREPLY=( $(compgen -W "$cmd_list" -- "$cur") )
}

complete -F _openafs_cmd_completion "$1"
