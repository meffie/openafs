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
 * Split strings using a shell-like syntax.
 */

#include <afsconfig.h>
#include <afs/param.h>

#include <roken.h>

#include <opr/queue.h>
#include <ctype.h>
#include <assert.h>

#include "cmd.h"

/* tokenize() token buffer. */
#define TOKEN_BUFFER_INITIAL_SIZE 256
struct token_buffer {
    char *buffer;        /**< Address of the allocated buffer. */
    size_t buffer_size;  /**< Current allocated buffer size. */
    size_t token_len;    /**< Current token length. */
    char *token_end;     /**< Address of the token nul terminator. */
};

/* cmd_Split() context. */
struct token_list {
    struct opr_queue q;
    int count;
};

/* cmd_Split() token elements. */
struct token_node {
    struct opr_queue q;
    char *token;
};

/**
 * Initialize an expandable token buffer.
 *
 * @param tb token buffer
 */
static int
init_token_buffer(struct token_buffer *tb)
{
    tb->buffer = calloc(TOKEN_BUFFER_INITIAL_SIZE, sizeof(*tb->buffer));
    if (tb->buffer == NULL)
	return ENOMEM;
    tb->buffer_size = TOKEN_BUFFER_INITIAL_SIZE;
    tb->token_len = 0;
    tb->token_end = tb->buffer;
    return 0;
}

/**
 * Clear the token buffer in preparation for the next token.
 *
 * @param tb token buffer
 */
static void
clear_token_buffer(struct token_buffer *tb)
{
    memset(tb->buffer, 0, tb->buffer_size);
    tb->token_end = tb->buffer;
    tb->token_len = 0;
}

/**
 * Free the token buffer.
 *
 * @param tb token buffer
 */
static void
free_token_buffer(struct token_buffer *tb)
{
    free(tb->buffer);
    tb->buffer = NULL;
    tb->buffer_size = 0;
    tb->token_end = NULL;
    tb->token_len = 0;
}

/**
 * Add a character to the token buffer.
 *
 * Realloc the token buffer if needed.
 *
 * @param tb token buffer
 * @param ch character to be added
 * @return 0 on success
 *   @retval ENOMEM  out of memory
 */
static int
accept_char(struct token_buffer *tb, char ch)
{
    if (tb->token_len + 1 == tb->buffer_size) {
	size_t space;
	tb->buffer_size *= 2;
	tb->buffer = realloc(tb->buffer, tb->buffer_size);
	if (tb->buffer == NULL)
	    return ENOMEM;
	/* Recalculate our end of token in the resized buffer. */
	tb->token_end = tb->buffer + tb->token_len;
	/* Clear from end of token to end of the resized buffer. */
	space = tb->buffer + tb->buffer_size - tb->token_end - 1;
	memset(tb->token_end + 1, 0, space * sizeof(*tb->token_end));
    }
    *tb->token_end++ = ch;
    tb->token_len++;
    return 0;
}

static int
accept_chars(struct token_buffer *tb, char *s)
{
    int code;
    for (; *s != '\0'; s++) {
	code = accept_char(tb, *s);
	if (code != 0)
	    return code;
    }
    return 0;
}

/**
 * Lexical analyzer for shell-like syntax.
 *
 * Convert a string into a series of tokens, splitting on whitespace, honoring
 * shell-like quoting, and backslash escape charaters (on unix-like systems).
 *
 * The 'emit' callback function is called each time a token is emitted. The
 * callback function should make a copy of the token if it is needed after the
 * callback returns.  The caller is responsible for freeing the copied token.
 *
 * @param[in] text  input string
 * @param[out] emit  called on each emitted token
 *
 * @return 0 on success
 *   @retval ENOMEM  out of memory
 *   @retval CMD_MISSINGQUOTE  missing closing quote in text
 *   @retval CMD_BADESCAPE  bad escape sequence in text
 */
static int
tokenize(const char *text, int (*emit)(char *token, void *rock), void *rock)
{
    int code;
    struct token_buffer tb;
    const char *tp;
    char quote = '\0';
    enum parse_state {
	STATE_READY,
	STATE_TOKEN,
	STATE_QUOTE,
#ifdef CMD_BACKSLASH_ESCAPE
	STATE_TOKEN_ESC,
	STATE_QUOTE_ESC,
#endif
    } state = STATE_READY;

    code = init_token_buffer(&tb);
    if (code != 0)
	return code;

    for (tp = text; *tp != '\0' && code == 0; tp++) {
	char ch = *tp;
	switch (state) {
	case STATE_READY:
	    if (isspace(ch)) {
		continue;
	    } else if (ch == '\'' || ch == '"') {
		quote = ch;
		state = STATE_QUOTE;
#ifdef CMD_BACKSLASH_ESCAPE
	    } else if (ch == '\\') {
		state = STATE_TOKEN_ESC;
#endif
	    } else {
		code = accept_char(&tb, ch);
		state = STATE_TOKEN;
	    }
	    break;
	case STATE_TOKEN:
	    if (isspace(ch)) {
		if (emit != NULL)
		    code = emit(tb.buffer, rock);
		clear_token_buffer(&tb);
		state = STATE_READY;
	    } else if (ch == '\'' || ch == '"') {
		quote = ch;
		state = STATE_QUOTE;
#ifdef CMD_BACKSLASH_ESCAPE
	    } else if (ch == '\\') {
		state = STATE_TOKEN_ESC;
#endif
	    } else {
		code = accept_char(&tb, ch);
		state = STATE_TOKEN;
	    }
	    break;
	case STATE_QUOTE:
	    if (ch == quote) {
		state = STATE_TOKEN;
	    } else {
		code = accept_char(&tb, ch);
	    }
	    break;
#ifdef CMD_BACKSLASH_ESCAPE
	case STATE_TOKEN_ESC:
	    code = accept_char(&tb, ch);
	    state = STATE_TOKEN;
	    break;
	case STATE_QUOTE_ESC:
	    code = accept_char(&tb, ch);
	    state = STATE_QUOTE;
	    break;
#endif
	default:
	    code = CMD_INTERNALERROR;
	    break;
	}
    }
    if (code == 0) {
	switch (state) {
	case STATE_READY:
	    break;
	case STATE_TOKEN:
	    if (emit != NULL)
		code = emit(tb.buffer, rock);
	    clear_token_buffer(&tb);
	    break;
	case STATE_QUOTE:
	    code = CMD_MISSINGQUOTE;
	    break;
#ifdef CMD_BACKSLASH_ESCAPE
	case STATE_TOKEN_ESC:
	    code = CMD_BADESCAPE;
	    break;
	case STATE_QUOTE_ESC:
	    code = CMD_MISSINGQUOTE;
	    break;
#endif
	default:
	    code = CMD_INTERNALERROR;
	    break;
	}
    }
    free_token_buffer(&tb);
    return code;
}

/**
 * Append a token to a list.
 *
 * @param token  token string
 * @param rock  callback context
 * @return 0 on success
 *   @retval ENOMEM  out of memory
 */
static int
append_token(char *token, void *rock)
{
    struct token_list *tokens = rock;
    struct token_node *node;

    node = calloc(1, sizeof(*node));
    if (node == NULL)
	return ENOMEM;
    node->token = strdup(token);
    if (node->token == NULL) {
	free(node);
	return ENOMEM;
    }
    tokens->count++;
    opr_queue_Append(&tokens->q, &node->q);
    return 0;
}

/**
 * Split a string using a shell-like syntax.
 *
 * The caller must free the argument strings with cmd_FreeArgv() and
 * then free the returned argv vector with free().
 *
 * @param[in] text     string to be split
 * @param[out] pargc   number of arguments
 * @param[out] pargv   argument string vector
 *
 * @return 0 on success
 *   @retval ENOMEM  out of memory
 *   @retval CMD_MISSINGQUOTE  missing closing quote in text
 *   @retval CMD_BADESCAPE  bad escape sequence in text
 */
int
cmd_Split(const char *text, int *pargc, char ***pargv)
{
    int code;
    struct token_list tokens;
    struct opr_queue *cursor, *store;
    int tc;
    char **tv;

    tokens.count = 0;
    opr_queue_Init(&tokens.q);
    code = tokenize(text, append_token, &tokens);
    if (code != 0)
	goto fail;

    /* Convert the list to an argv string vector. */
    tc = 0;
    tv = calloc(tokens.count + 1, sizeof(*tv));
    for (opr_queue_ScanSafe(&tokens.q, cursor, store)) {
	struct token_node *n = opr_queue_Entry(cursor, struct token_node, q);
	tv[tc++] = n->token;
	free(n);
    }

    *pargc = tokens.count;
    *pargv = tv;
    return 0;

  fail:
    for (opr_queue_ScanSafe(&tokens.q, cursor, store)) {
	struct token_node *n = opr_queue_Entry(cursor, struct token_node, q);
	free(n->token);
	free(n);
    }
    *pargc = 0;
    *pargv = NULL;
    return code;
}

/**
 * Free the string vector returned from cmd_Split()
 *
 * @param pargv  pointer a the string vector allocated by cmd_Split()
 */
void
cmd_FreeSplit(char ***pargv)
{
    if (*pargv != NULL) {
        for (char **arg = *pargv; *arg != NULL; arg++) {
	    free(*arg);
	    *arg = NULL;
	}
	free(*pargv);
	*pargv = NULL;
    }
}

/**
 * Returns true if the string does not need to be quoted in a command line.
 *
 * @param s  string to check
 * @return  non-zero if string is safe without quotes
 */
static int
has_safe_chars(char *s)
{
    const char *safe = "0123456789"
		       "abcdefghijklmnopqrstuvwxyz"
		       "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		       "@%+=:,./-";
    size_t len = strlen(s);
    return (strspn(s, safe) == len);
}

/**
 * Join strings into a shell-like command string.
 *
 * Join an argv string vector into a string quoted for a command line. Arguments
 * which required quotes are enclosed in single quotes. Single quote characters
 * are quoted with double quotes, so string a'b is quoted as 'a'"'"'b'
 *
 * @param[in] argc  argument count
 * @param[in] argv  arguments to be joined
 * @param[out] text  joined output; must be freed by the caller
 */
int
cmd_Join(int argc, char **argv, char **text)
{
    int code;
    struct token_buffer tb;

    *text = NULL;
    code = init_token_buffer(&tb);
    if (code != 0)
	return code;

    for (int i = 0; i < argc; i++) {
	if (i > 0)
	    accept_char(&tb, ' ');
	if (has_safe_chars(argv[i])) {
	    code = accept_chars(&tb, argv[i]);
	    if (code != 0)
		goto fail;
	} else {
	    /* Quote the argument. */
	    code = accept_char(&tb, '\'');
	    if (code != 0)
		goto fail;
	    for (char *p = argv[i]; *p != '\0'; p++) {
		if (*p == '\'') {
		    code = accept_chars(&tb, "'\"'\"'");
		    if (code != 0)
			goto fail;
		} else {
		    code = accept_char(&tb, *p);
		    if (code != 0)
			goto fail;
		}
	    }
	    accept_char(&tb, '\'');
	    if (code != 0)
		goto fail;
	}
    }
    code = 0;
    *text = strdup(tb.buffer);
  fail:
    free_token_buffer(&tb);
    return code;
}
