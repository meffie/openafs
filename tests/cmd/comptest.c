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
command_foo(struct cmd_syndesc *as, void *arock)
{
    printf("Running foo\n");
    return 0;
}

static int
command_bar(struct cmd_syndesc *as, void *arock)
{
    printf("Running bar\n");
    return 0;
}

int
main(int argc, char *argv[])
{
    int code;
    struct cmd_syndesc *syntax;

    syntax = cmd_CreateSyntax("foo", command_foo, NULL, 0, "command foo");
    cmd_AddParm(syntax, "-example", CMD_FLAG, CMD_OPTIONAL, "example flag");

    syntax = cmd_CreateSyntax("bar", command_bar, NULL, 0, "command bar");
    cmd_AddParm(syntax, "-option", CMD_SINGLE, CMD_REQUIRED, "example option");

    code = cmd_Dispatch(argc, argv);
    return code;
}
