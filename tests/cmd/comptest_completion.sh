# Bash completion function that calls comptest with -completion-helper, the number of words and the array of words
# to get the list of possible completions based on the current command line context, then uses compgen to filter
# the list based on the current word.

_comptest_completion()
{
	local cur="${COMP_WORDS[COMP_CWORD]}"

	local cmd_list=$(./comptest -completion-helper -- "$COMP_CWORD" "${COMP_WORDS[@]}" 2>/tmp/comptest.err)
	COMPREPLY=( $(compgen -W "$cmd_list" -- "$cur") )
}

complete -F _comptest_completion ./comptest
