/*
 * Copyright (c) 2026 Sine Nomine Associates. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR `AS IS'' AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * This is a sample program to test shell tab completions.
 */

#include <afsconfig.h>
#include <afs/param.h>
#include <roken.h>
#include <afs/cmd.h>

static int
command_proc(struct cmd_syndesc *as, void *arock)
{
    return 0;
}

int
main(int argc, char *argv[])
{
    int code;
    struct cmd_syndesc *syntax;

    syntax = cmd_CreateSyntax("one", command_proc, NULL, 0, "test command one");
    cmd_AddParm(syntax, "-apple", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-banana", CMD_SINGLE, CMD_REQUIRED, "example");
    cmd_AddParm(syntax, "-peach", CMD_LIST, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-pear", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-plum", CMD_SINGLE, CMD_OPTIONAL, "example");

    syntax = cmd_CreateSyntax("two", command_proc, NULL, 0, "test command two");
    cmd_AddParm(syntax, "-apple", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-banana", CMD_SINGLE, CMD_REQUIRED, "example");
    cmd_AddParm(syntax, "-peach", CMD_LIST, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-orange", CMD_SINGLE, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-lime", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_CreateAlias(syntax, "duo");

    syntax = cmd_CreateSyntax("three", command_proc, NULL, 0, "test command three");
    cmd_AddParm(syntax, "-apple", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-banana", CMD_SINGLE, CMD_REQUIRED, "example");
    cmd_AddParm(syntax, "-peach", CMD_LIST, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-lime", CMD_FLAG, CMD_OPTIONAL, "example");

    syntax = cmd_CreateSyntax("four", command_proc, NULL, 0, "test command four");
    cmd_AddParm(syntax, "-apple", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-banana", CMD_SINGLE, CMD_REQUIRED, "example");
    cmd_AddParm(syntax, "-peach", CMD_LIST, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-lime", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-kiwi", CMD_FLAG, CMD_OPTIONAL, "example");

    syntax = cmd_CreateSyntax("five", command_proc, NULL, 0, "test command five");
    cmd_AddParm(syntax, "-apple", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-banana", CMD_SINGLE, CMD_REQUIRED, "example");
    cmd_AddParm(syntax, "-peach", CMD_LIST, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-pear", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-kiwi", CMD_FLAG, CMD_OPTIONAL, "example");
    cmd_AddParm(syntax, "-mango", CMD_FLAG, CMD_OPTIONAL, "example");


    code = cmd_Dispatch(argc, argv);
    return code;
}
