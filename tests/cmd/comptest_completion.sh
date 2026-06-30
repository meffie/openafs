_comptest_completion_commands()
{
	local prev="$1"
	local cur="$2"

	case "$prev" in
                "./comptest")
                        echo "apropos bar foo help version"
                        ;;
                "foo")
                        echo "-example -help"
                        ;;
                "bar")
                        echo "-option -help"
                        ;;
                "version")
                        echo "-help"
                        ;;
                "help"|"apropos")
                        echo "-help -topic"
                        ;;
                "-example"|"-option"|"-topic")
                        if [[ "$cur" == -* ]]; then
                                echo "-help"
                        fi
                        ;;

        esac
}

_comptest_completion()
{
	local cur="${COMP_WORDS[COMP_CWORD]}"
	local prev="${COMP_WORDS[COMP_CWORD-1]}"

	local cmd_list=$(./comptest -completion-helper -- "$prev" "$cur" 2>/tmp/comptest.err)
	COMPREPLY=( $(compgen -W "$cmd_list" -- "$cur") )
}

complete -F _comptest_completion ./comptest
