/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 *
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 */

#include "afsconfig.h"

#define	MAXLINELEN	1024
#define	MAXTOKLEN	100
#include <sys/param.h>
#include <sys/types.h>
#include <sys/file.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

#define TOK_DONTUSE 1		/* Don't copy if match and this flag is set. */
struct token {
    struct token *next;
    char *key;
    int flags;
};

/**
 * Parse the directive line into a set of words.
 *
 * Extract the sysname, arch, and OS words from a directive line.  The words are
 * enclosed by '<' and '>' characters. Words staring with a '-' symbol are
 * placed in the negative set.
 *
 * This function splits the 'aline' input string in place.
 *
 * @param aline directive line
 * @param alist list of tokens
 */
static int
ParseDirective(char *aline, struct token **alist)
{
    struct token *head = NULL;
    struct token *tail = NULL;
    const char *sep = " \t\r\n";
    char *end;
    char *word;

    /*
     * Extract the string enclosed by the '<' and '>' markers.  The leading '<'
     * must be the first character of the line and the enclosing '>' should be
     * the last character of the line. Any characters following the '>' end
     * marker are ignored.
     */
    if (aline[0] != '<')
	return -1;
    aline++;
    end = strchr(aline, '>');
    if (end == NULL)
	return -1;
    *end = '\0';

    /*
     * Split the words delimited by whitespace. Words starting with the '-'
     * symbol are put into the negative set.
     */
    for (word = strtok(aline, sep); word != NULL; word = strtok(NULL, sep)) {
	struct token *token = calloc(1, sizeof(*token));
	if (token == NULL)
	    return ENOMEM;
	if (word[0] == '-') {
	    token->key = word + 1;
	    token->flags = TOK_DONTUSE;
	} else {
	    token->key = word;
	    token->flags = 0;
	}
	if (head == NULL)
	    head = token;
	else
	    tail->next = token;
	tail = token;
    }
    *alist = head;
    return 0;
}

/**
 * Free token list returned by ParseDirective().
 */
static int
FreeTokens(struct token *alist)
{
    struct token *nlist;
    for (; alist; alist = nlist) {
	nlist = alist->next;
	free(alist);
    }
    return 0;
}

/* read a line into a buffer, putting in null termination and stopping on appropriate
    end of line char.  Returns 0 at eof, > 0 at normal line end, and < 0 on error */
static int
GetLine(FILE * afile, char *abuffer, int amax)
{
    int tc;
    int first;

    first = 1;
    while (1) {
	tc = getc(afile);
	if (first && tc < 0)
	    return 0;
	first = 0;
	if (tc <= 0 || tc == '\012') {
	    if (amax > 0)
		*abuffer++ = 0;
	    return (amax > 0 ? 1 : -1);
	}
	if (amax > 0) {
	    /* keep reading to end of line so next one isn't bogus */
	    *abuffer++ = tc;
	    amax--;
	}
    }
}

int
mc_copy(FILE * ain, FILE * aout, char *alist[])
{
    char tbuffer[MAXLINELEN];
    struct token *tokens;
    char **tp;
    struct token *tt;
    int code;
    int copying;
    int done;
    int line_number = 1;

    copying = 1;		/* start off copying data */
    while (1) {
	/* copy lines, handling modes appropriately */
	code = GetLine(ain, tbuffer, MAXLINELEN);
	if (code <= 0)
	    break;
	/* otherwise process the line */
	if (tbuffer[0] == '<') {
	    /* interpret the line as a set of options, any one of which will cause us
	     * to start copying the data again. */
	    code = ParseDirective(tbuffer, &tokens);
	    if (code != 0) {
		fprintf(stderr, "Failed to parse directive on line %d.\n", line_number);
		return -1;
	    }
	    copying = 0;
	    done = 0;
	    for (tp = alist; (!done) && (*tp != NULL); tp++) {
		for (tt = tokens; tt; tt = tt->next) {
		    if (!strcmp(*tp, tt->key)) {
			/* Need to search all tokens in case a dont use
			 * flag is set. But we can stop on the first
			 * don't use.
			 */
			if (tt->flags & TOK_DONTUSE) {
			    copying = 0;
			    done = 1;
			    break;
			} else {
			    copying = 1;
			}
		    }
		}
	    }
	    FreeTokens(tokens);
	} else {
	    /* just copy the line */
	    if (copying) {
		fwrite(tbuffer, 1, strlen(tbuffer), aout);
		putc('\n', aout);
	    }
	}
	line_number++;
    }
    return 0;
}
