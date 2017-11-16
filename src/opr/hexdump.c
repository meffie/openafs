/*
 * Copyright (C) 2017 Sine Nomine Associates
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * * Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 *
 * * Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in
 *   the documentation and/or other materials provided with the
 *   distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <afsconfig.h>
#include <afs/param.h>

#include <roken.h>
#include <ctype.h>

/*!
 * Hex dump for debugging.
 */
void
opr_hexdump(FILE *stream, void *data, int len)
{
    int i, j;
    unsigned char *byte = (unsigned char *)data;
    unsigned char ascii[17];

    ascii[0] = '\0';
    for (i = 0, j = 0; i < len; i++, byte++) {
	if (j == 0)
	    fprintf(stream, "  %04x ", i);
	fprintf(stream, " %02x", *byte);
	if (j == 7)
	    printf(" ");
	if (isascii(*byte))
	    ascii[j++] = *byte;
	else
	    ascii[j++] = '.';
	ascii[j] = '\0';
	if (j == 16) {
	    printf("  %s\n", ascii);
	    j = 0;
	    ascii[0] = '\0';
	}
    }
    if (ascii[0] != '\0') {
	for (; j < 16; j++) {
	    if (j == 7)
	       fprintf(stream, "    ");
	    else
	       fprintf(stream, "   ");
	}
	fprintf(stream, "  %s\n", ascii);
    }
}
