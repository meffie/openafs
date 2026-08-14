# OpenAFS Shell Completion

This directory contains shell completion support for OpenAFS commands.

Completion is currently provided for Bash and Zsh. The completion scripts
use the OpenAFS `cmd` library to obtain completion candidates directly from
the command syntax definitions.

## How it works

Commands built with `libcmd` support an internal `-completion-helper` option. When called with this option, instead of running normally, the command prints a list of possible completions for the current word being typed, based on the command's syntax (subcommands and options).

The helper is invoked in the following form:

    command -completion-helper -- COMP_CWORD COMP_WORDS

For example:

    $ vos -completion-helper -- 2 vos create -
    -server -partition -name -maxquota -id -roid -cell -noauth
    -localauth -verbose -encrypt -noresolve -config -rxgk -help


In Bash, the command-line context is provided through `COMP_WORDS` and
`COMP_CWORD`. The Zsh completion script maps Zsh's corresponding completion
state to the same interface.

The shell completion scripts call this option internally when the user
presses TAB and use the output to populate the list of suggestions.

## Usage

Source the appropriate script for your shell:

    $ source openafs_completion.bash
    $ source openafs_completion.zsh

This registers completion for all supported OpenAFS commands listed in
the script.

## Supported commands

The completion scripts currently register the following commands:

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

Commands that do not use the OpenAFS `cmd` library or otherwise do not
support the `-completion-helper` interface, cannot use this completion
mechanism. Known examples include `aklog` and `asetkey`.

## Limitations

Completion currently provides subcommand and option-name
completion. It does not complete values for options.

For example, after:

    vos create -server <TAB>

the completion helper knows that `-server` expects a value and therefore
does not offer other option names, but it does not attempt to discover or
complete valid server names.

The same applies to values for `CMD_SINGLE` and `CMD_LIST` parameters,
such as server names, partition names, volume names, cell names or other
values that depend on the current OpenAFS environment.

Some OpenAFS commands also support positional shortcut syntax. For example,
these forms of `vos create` are equivalent:

    vos create -server a -partition b -name c
    vos create a b c

The completion helper does not currently model these positional mappings. It does not identify which parameter a positional argument corresponds to.

Since completion is based on the syntax registered with the `cmd` library, new subcommands and options of an already supported command are automatically available to the completion helper. New command executables
must still be added to the command list in the shell completion scripts.