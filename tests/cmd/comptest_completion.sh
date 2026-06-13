_comptest_completion()
{
	local cur="${COMP_WORDS[COMP_CWORD]}"
	local prev="${COMP_WORDS[COMP_CWORD-1]}"
	local commands="apropos bar foo help version"
	local commands_foo="-example -help"
	local commands_bar="-option -help"

	case "$prev" in
		"./comptest")
			COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
			;;
		"foo")
			COMPREPLY=( $(compgen -W "$commands_foo" -- "$cur") )
			;;
		"bar")
			COMPREPLY=( $(compgen -W "$commands_bar" -- "$cur") )
			;;
		"version")
			COMPREPLY=( $(compgen -W "-help" -- "$cur") )
                        ;;
		"help"|"apropos")
                        COMPREPLY=( $(compgen -W "-help -topic" -- "$cur") )
                        ;;
		"-example"|"-option"|"-topic")
			if [[ "$cur" == -* ]]; then
                                COMPREPLY=( $(compgen -W "-help" -- "$cur") )
			fi
			;;

	esac
}

complete -F _comptest_completion ./comptest
