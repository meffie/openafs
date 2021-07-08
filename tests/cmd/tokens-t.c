/*
 * Copyright 2021, Sine Nomine Associates and others.
 * All Rights Reserved.
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

/*
 * Tests for cmd_Split(), cmd_Join(), and cmd_ParseLine().
 */

#include <afsconfig.h>
#include <afs/param.h>
#include <roken.h>
#include <afs/cmd.h>
#include <tests/tap/basic.h>

struct good_case {
    char *text;
    char *quoted; /* Normalized quoted. */
    int argc;
    char *argv[16];
} good_cases[] = {
    {"", NULL, 0, {NULL}},
    {"a", NULL, 1, {"a", NULL}},
    {"a bc def", NULL, 3, {"a", "bc", "def", NULL}},

    {"''", "", 1, {"", NULL}},
    {"\"\"", "", 1, {"", NULL}},
    {"''\"\"''", "", 1, {"", NULL}},

    {"\"don't worry\", be happy.", "'don'\"'\"'t worry,' be happy.",
	3, {"don't worry,", "be", "happy.", NULL}},
    {"'a b'", NULL, 1, {"a b", NULL}},
    {"\"a b\"", "'a b'", 1, {"a b", NULL}},
    {"'a'\"'\"'b'", NULL, 1, {"a'b", NULL}},
    {"'a'\"'\"'b cd'", "'a'\"'\"'b cd'", 1, {"a'b cd", NULL}},
    {"a 'bc def'", NULL, 2, {"a", "bc def", NULL}},
    {"a \"bc def\"", "a 'bc def'", 2, {"a", "bc def", NULL}},
    {"a 'b c' def", NULL, 3, {"a", "b c", "def", NULL}},
    {"a b\" \"c def", "a 'b c' def", 3, {"a", "b c", "def", NULL}},
    {"a''b", "ab", 1, {"ab", NULL}},
    {"a b 'c \"d e\"f' g", NULL, 4, {"a", "b", "c \"d e\"f", "g", NULL}},
    {"a b \"c 'de\" g", "a b 'c '\"'\"'de' g", 4, {"a", "b", "c 'de", "g", NULL}},

#ifdef CMD_BACKSLASH_ESCAPE
    {"a\\ b", "'a b'", 1, {"a b", NULL}},
    {"a \\'bc", "a ''\"'\"'bc'", 2, {"a", "'bc", NULL}},
    {"a \\\"bc", "a '\"bc'", 2, {"a", "\"bc", NULL}},
    {"a b\\'c", "a 'b'\"'\"'c'", 2, {"a", "b'c", NULL}},
    {"a b\\\"c", "a 'b\"c'", 2, {"a", "b\"c", NULL}},
    {"a 'b\\ c'", NULL, 2, {"a", "b\\ c", NULL}},
    {"a \"b\\ c\"", "a 'b\\ c'", 2, {"a", "b\\ c", NULL}},
    {"a 'b\\\"c'", NULL, 2, {"a", "b\\\"c", NULL}},
#else
    {"a\\ b", "'a\\' b", 2, {"a\\", "b", NULL}},
    {"a \\'bc'", "a '\\bc'", 2, {"a", "\\bc", NULL}},
    {"a \\\"bc\"", "a '\\bc'", 2, {"a", "\\bc", NULL}},
    {"a b\\'c'", "a 'b\\c'", 2, {"a", "b\\c", NULL}},
    {"a b\\\"c\"", "a 'b\\c'", 2, {"a", "b\\c", NULL}},
    {"a 'b\\ c'", NULL, 2, {"a", "b\\ c", NULL}},
    {"a \"b\\ c\"", "a 'b\\ c'", 2, {"a", "b\\ c", NULL}},
    {"a 'b\\\"c'", NULL, 2, {"a", "b\\\"c", NULL}},
#endif

    {NULL, NULL, 0, {NULL}}, /* End of tests. */
};

struct bad_case {
    char *text;
    int code;
} bad_cases[] = {
    {"'", CMD_MISSINGQUOTE},
    {"\"", CMD_MISSINGQUOTE},
    {"\"bcdef", CMD_MISSINGQUOTE},
    {"'bcdef", CMD_MISSINGQUOTE},
    {"'\"\"bcd", CMD_MISSINGQUOTE},
    {"a bcd 'ef", CMD_MISSINGQUOTE},

#ifdef CMD_BACKSLASH_ESCAPE
    {"abc\\", CMD_BADESCAPE},
    {"ab'c\\", CMD_MISSINGQUOTE},
#else
    {"abc\\'", CMD_MISSINGQUOTE},
    {"ab\\'c", CMD_MISSINGQUOTE},
#endif

    {NULL, 0}, /* End of tests. */
};

void
test_split(void)
{
    int code;
    int tc;
    char **tv;

    for (struct good_case *t = good_cases; t->text; t++) {
	tc = -1;
	tv = NULL;
	code = cmd_Split(t->text, &tc, &tv);
	is_int(code, 0, "cmd_Split: %s", t->text);
	if (tv == NULL)
	    bail("cmd_Split() failed code=%d text=%s", code, t->text);
	is_int(tc, t->argc, ".. size is %d", t->argc);
	for (int i = 0; i <= t->argc && i <= tc; i++) {
	    is_string(tv[i], t->argv[i], ".. argv[%d] is %s", i, t->argv[i]);
	}
	cmd_FreeSplit(&tv);
    }

    for (struct bad_case *t = bad_cases; t->text; t++) {
	tc = -1;
	tv = NULL;
	code = cmd_Split(t->text, &tc, &tv);
	is_int(code, t->code, "cmd_Split: %s", t->text);
	cmd_FreeSplit(&tv);
    }
}

void
test_join(void)
{
    int code;

    for (struct good_case *t = good_cases; t->text; t++) {
	char *text = NULL;
	char *want = t->quoted ? t->quoted : t->text;

	code = cmd_Join(t->argc, t->argv, &text);
	if (code != 0)
	    is_int(code, 0, "cmd_Join: %s", want);
	else
	    is_string(text, want, "cmd_Join: %s", want);
	free(text);
    }
}

void
test_parseline(void)
{
    int code;
    int tc;
    char *tv[100];

    /*
     * Note: argv[0] should be an empty placeholder string, so we shift the
     *       argv checks by one.
     */
    for (struct good_case *t = good_cases; t->text; t++) {
	tc = -1;
	memset(tv, 0, sizeof(tv));
	code = cmd_ParseLine(t->text, tv, &tc, sizeof(tv)/sizeof(*tv));
	is_int(code, 0, "cmd_ParseLine: %s", t->text);
	is_int(tc, t->argc + 1, ".. size is %d", t->argc);
	is_string(tv[0], "", ".. argv[0] is '' (placeholder)");
	for (int i = 0; i < sizeof(tv)/sizeof(*tv) && i <= t->argc; i++) {
	    is_string(tv[i+1], t->argv[i], ".. argv[%d] is %s", i, t->argv[i]);
	}
	cmd_FreeArgv(tv);
    }

    for (struct bad_case *t = bad_cases; t->text; t++) {
	tc = -1;
	memset(tv, 0, sizeof(tv));
	code = cmd_ParseLine(t->text, tv, &tc, sizeof(tv)/sizeof(*tv));
	is_int(code, t->code, "cmd_ParseLine: %s", t->text);
	cmd_FreeArgv(tv);
    }

    /* CMD_TOOMANY test */
    code = cmd_ParseLine("a b", tv, &tc, 2);
    is_int(code, CMD_TOOMANY, "cmd_ParseLine: too many");
}

int
main(int argc, char **argv)
{
    plan(321);
    initialize_CMD_error_table();
    test_split();
    test_join();
    test_parseline();
    return 0;
}
