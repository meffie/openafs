_comptest_completion()
{
	local cur="${COMP_WORDS[COMP_CWORD]}"

	local cmd_list=$(./comptest -completion-helper -- "$COMP_CWORD" "${COMP_WORDS[@]}" 2>/tmp/comptest.err)
	COMPREPLY=( $(compgen -W "$cmd_list" -- "$cur") )
}

complete -F _comptest_completion ./comptest
