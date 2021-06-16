/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 * 
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 */

#include <afsconfig.h>
#include <afs/param.h>

#include <stdio.h>
#ifdef HAVE_STDLIB_H
#include <stdlib.h>
#endif
#include <time.h>

#include <afs/ktime.h>
#include <afs/afsutil.h>
#include <afs/afsutil_prototypes.h>
#include <tests/tap/basic.h>

static struct testTime {
    char *time;
    long code;
    time_t sec;
} testTimes[] = {
    { "now",                1,  0 }, /* lookup current time */
    { "never",              0,  (afs_int32) -1 },
    { "12/3/89",            0,  628664400 },
    { "1/1/1",              0,  978325200 },
    { "1/0/80",             -2, 0 },
    { "13/1/80",            -2, 0 },
    { "0/1/80",             -2, 0 },
    { "1/32/80",            -2, 0 },
    { "2/30/80",            0,  320734799 },
    /*
     * Oh, well: note that 2/30 is bigger than any real date in February, and
     * since this algorithm approaches the correct value from below, this is
     * the closest it can come.
     */
    { "3/1/80",             0,  320734800 },
    { "3/1/80 0:00",        0,  320734800 },
    { "2/30/80 24:00",      -2, 0 },
    { "2/30/80 23:60",      -2, 0 },
    { "22/22/22",           -2, 0 },
    { "12/31/69 19:07",     0,  420 },
    { "12/31/99 23:59",     0,  946702740 },
    { "12/31/99 23:59:59",  0,  946702799 },
    { "23:12",              -1, 0 },
    { "22/12",              -1, 0 },
    { "22/22/22 12",        -1, 0 },
    { "12/31/199 23:59:59", -2, 0 },
    { "12/31/1888",         -2, 0 },
    { "-13/-44/22 -15:77",  -2, 0 },
    { "4/14/24",            0,  1713070800 },
    { "4/14/2024",          0,  1713070800 },
    { "4/14/68",            0,  0x7fffffff }, /* legal but w/sign bit on */
    { "4/14/69",            0,  0 },
    { NULL,                 0,  0 }
};

static struct testPeriodic {
    char *date;
    int code;
    struct ktime kt;
} testPeriodics[] = {
    /* Special now and never. */
    {"now", 0, {KTIME_NOW, 0, 0, 0, 0}},
    {"never", 0, {KTIME_NEVER, 0, 0, 0, 0}},
    {"  never  ", 0, {KTIME_NEVER, 0, 0, 0, 0}},

    /* 24 hour times */
    {"1", 0, {KTIME_HOUR | KTIME_MIN | KTIME_SEC, 1, 0, 0, 0}},
    {"12:00", 0, {KTIME_HOUR | KTIME_MIN | KTIME_SEC, 12, 0, 0, 0}},
    {"23:59:59",  0, {KTIME_HOUR | KTIME_MIN| KTIME_SEC, 23, 59, 59, 0}},

    /* 12 hour times */
    {"2:00 am",  0, {KTIME_HOUR | KTIME_MIN | KTIME_SEC, 2, 0, 0, 0}},
    {"2:00 a.m.",  0, {KTIME_HOUR | KTIME_MIN | KTIME_SEC, 2, 0, 0, 0}},
    {"2:00 pm",  0, {KTIME_HOUR | KTIME_MIN | KTIME_SEC, 14, 0, 0, 0}},
    {"2:00 p.m.",  0, {KTIME_HOUR | KTIME_MIN | KTIME_SEC, 14, 0, 0, 0}},

    /* Days */
    {"sun", 0, {KTIME_DAY, 0, 0, 0, 0}},
    {"mon", 0, {KTIME_DAY, 0, 0, 0, 1}},
    {"tue", 0, {KTIME_DAY, 0, 0, 0, 2}},
    {"wed", 0, {KTIME_DAY, 0, 0, 0, 3}},
    {"thu", 0, {KTIME_DAY, 0, 0, 0, 4}},
    {"thur", 0, {KTIME_DAY, 0, 0, 0, 4}},
    {"fri", 0, {KTIME_DAY, 0, 0, 0, 5}},
    {"sat", 0, {KTIME_DAY, 0, 0, 0, 6}},
    {"sunday", 0, {KTIME_DAY, 0, 0, 0, 0}},
    {"monday", 0, {KTIME_DAY, 0, 0, 0, 1}},
    {"tuesday", 0, {KTIME_DAY, 0, 0, 0, 2}},
    {"wednesday", 0, {KTIME_DAY, 0, 0, 0, 3}},
    {"thursday", 0, {KTIME_DAY, 0, 0, 0, 4}},
    {"friday", 0, {KTIME_DAY, 0, 0, 0, 5}},
    {"saturday", 0, {KTIME_DAY, 0, 0, 0, 6}},
    {"every saturday", 0, {KTIME_DAY, 0, 0, 0, 6}},

    /* Compound */
    {"every tuesday at 2:15 am", 0,
	{KTIME_DAY | KTIME_HOUR | KTIME_MIN | KTIME_SEC, 2, 15, 0, 2}},
    {"friday at 8:00 pm", 0,
	{KTIME_DAY | KTIME_HOUR | KTIME_MIN | KTIME_SEC, 20, 0, 0, 5}},

    /* Syntax errors, but silently fail. */
    {"", 0, {0, 0, 0, 0, 0}},
    {"  ", 0, {0, 0, 0, 0, 0}},

    /* Syntax */
    {"bogus", -1, {0, 0, 0, 0, 0}},
    {"99:99",  -1, {KTIME_HOUR | KTIME_MIN| KTIME_SEC, 99, 99, 0, 0}},

    /* End of tests. */
    {NULL, 0, {0, 0, 0, 0, 0}}
};


/**
 * Compare ktime.
 */
void
is_ktime(struct ktime *expect, struct ktime *got)
{
    is_int(expect->mask, got->mask, ".. mask is 0x%02d", expect->mask);
    is_int(expect->hour, got->hour, ".. hour is %d", expect->hour);
    is_int(expect->min, got->min, ".. min is %d", expect->min);
    is_int(expect->sec, got->sec, ".. sec is %d", expect->sec);
    is_int(expect->day, got->day, ".. day is %d", expect->day);
}

int
main(void)
{
    long code;
    afs_int32 temp;
    time_t t;
    struct testTime *tt;
    struct testPeriodic *tp;

    plan(246);

    /* should do timezone and daylight savings time correction so this program
     * work in other than EST */
    putenv("TZ=EST+5");

    for (tt = testTimes; tt->time; tt++) {
	temp = 0;
	code = ktime_DateToLong(tt->time, &temp);
	t = temp;
        if (tt->code == 1) {
            is_int(0, code, "ktime_DateToLong return for %s", tt->time);
            ok((time(0) - t <= 1), "ktime_DateToLong result for %s", tt->time);
        } else {
            is_int(tt->code, code, "ktime_DateToLong return for %s", tt->time);
            is_int(tt->sec, t, "ktime_DateToLong result for %s", tt->time);
        }
    }

    for (tp = testPeriodics; tp->date; tp++) {
	struct ktime kt;
	memset(&kt, -1, sizeof(kt));
	code = ktime_ParsePeriodic(tp->date, &kt);
	is_int(tp->code, code, "ktime_ParsePeriodic return for '%s'", tp->date);
	is_ktime(&tp->kt, &kt);
    }

    return 0;
}
