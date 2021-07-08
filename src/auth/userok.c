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
#include <afs/stds.h>

#include <roken.h>
#include <afs/opr.h>

#include <ctype.h>

#include <afs/pthread_glock.h>
#include <rx/xdr.h>
#include <rx/rx.h>
#include <rx/rx_identity.h>
#ifdef AFS_RXGK_ENV
# include <rx/rxgk.h>
#endif
#include <afs/afsutil.h>
#include <afs/fileutil.h>

#include "base64.h"
#include "auth.h"
#include "cellconfig.h"
#include "keys.h"
#include "afs/audit.h"

/* The display names for localauth and noauth identities; they aren't used
 * inside tickets or anything, but just serve as something to display in logs,
 * etc. */
#define AFS_LOCALAUTH_NAME "<LocalAuth>"
#define AFS_LOCALAUTH_LEN  (sizeof(AFS_LOCALAUTH_NAME)-1)
#define AFS_NOAUTH_NAME "<NoAuth>"
#define AFS_NOAUTH_LEN  (sizeof(AFS_NOAUTH_NAME)-1)

/*
 * Maximum UserList file line buffer size. Includes a truncation check
 * character, optional newline, and terminating nul character.
 */
#define USERLIST_MAXLINESIZE 2048

static int ParseLine(char *buffer, struct rx_identity *user);
static int GetIdentity(struct afsconf_dir *dir,
		       struct rx_identity **identity,
		       int (*compare)(struct rx_identity *id, void *rock),
		       void *rock);

struct cursor {
    int index;
    int target;
};

static int
id_at_index(struct rx_identity *id, void *rock)
{
    struct cursor *cursor = rock;
    return (cursor->index++ == cursor->target);
}

static int
user_at_index(struct rx_identity *id, void *rock)
{
    struct cursor *cursor = rock;
    if (id->kind != RX_ID_KRB4)
	return 0;  /* Count legacy entries only. */
    return (cursor->index++ == cursor->target);
}

static int
id_matches(struct rx_identity *id, void *rock)
{
    struct rx_identity *target = rock;
    return rx_identity_match(id, target);
}

int
afsconf_CheckAuth(void *arock, struct rx_call *acall)
{
    struct afsconf_dir *adir = (struct afsconf_dir *) arock;
    int rc;
    LOCK_GLOBAL_MUTEX;
    rc = ((afsconf_SuperUser(adir, acall, NULL) == 0) ? 10029 : 0);
    UNLOCK_GLOBAL_MUTEX;
    return rc;
}

static int
GetNoAuthFlag(struct afsconf_dir *adir)
{
    if (access(AFSDIR_SERVER_NOAUTH_FILEPATH, 0) == 0) {
	osi_audit(NoAuthEvent, 0, AUD_END);	/* some random server is running noauth */
	return 1;		/* if /usr/afs/local/NoAuth file exists, allow access */
    }
    return 0;
}


int
afsconf_GetNoAuthFlag(struct afsconf_dir *adir)
{
    int rc;

    LOCK_GLOBAL_MUTEX;
    rc = GetNoAuthFlag(adir);
    UNLOCK_GLOBAL_MUTEX;
    return rc;
}

void
afsconf_SetNoAuthFlag(struct afsconf_dir *adir, int aflag)
{
    afs_int32 code;

    LOCK_GLOBAL_MUTEX;
    if (aflag == 0) {
	/* turn off noauth flag */
	code = (unlink(AFSDIR_SERVER_NOAUTH_FILEPATH) ? errno : 0);
	osi_audit(NoAuthDisableEvent, code, AUD_END);
    } else {
	/* try to create file */
	code =
	    open(AFSDIR_SERVER_NOAUTH_FILEPATH, O_CREAT | O_TRUNC | O_RDWR,
		 0666);
	if (code >= 0) {
	    close(code);
	    osi_audit(NoAuthEnableEvent, 0, AUD_END);
	} else
	    osi_audit(NoAuthEnableEvent, errno, AUD_END);
    }
    UNLOCK_GLOBAL_MUTEX;
}

/*!
 * Remove an identity from the UserList file
 *
 * This function removes the given identity from the user list file.
 * For the purposes of identifying entries to remove, only the
 * type and exportedName portions of the identity are used. Callers
 * should remember that a given identity may be listed in the file in
 * a number of different ways.
 *
 * @param adir
 * 	A structure representing the configuration directory currently
 * 	in use
 * @param user
 * 	The RX identity to delete
 *
 * @returns
 * 	0 on success, an error code on failure
 */

int
afsconf_DeleteIdentity(struct afsconf_dir *adir, struct rx_identity *user)
{
    char *filename = NULL;
    char *nfilename = NULL;
    char *buffer = NULL;
    char *copy;
    FILE *tf = NULL;
    FILE *nf = NULL;
    int flag;
    char *tp;
    int found;
    struct stat tstat;
    struct rx_identity identity;
    afs_int32 code;

    memset(&identity, 0, sizeof(struct rx_identity));

    LOCK_GLOBAL_MUTEX;

    buffer = calloc(USERLIST_MAXLINESIZE, sizeof(*buffer));
    if (buffer == NULL) {
	code = ENOMEM;
	goto out;
    }

    code = asprintf(&filename, "%s/%s", adir->name, AFSDIR_ULIST_FILE);
    if (code < 0) {
	code = ENOMEM;
	goto out;
    }
#ifndef AFS_NT40_ENV
    {
	/*
	 * We attempt to fully resolve this pathname, so that the rename
	 * of the temporary file will work even if UserList is a symlink
	 * into a different filesystem.
	 */
	nfilename = malloc(AFSDIR_PATH_MAX);
	if (nfilename == NULL) {
	    code = ENOMEM;
	    goto out;
	}
	if (realpath(filename, nfilename)) {
	    free(filename);
	    filename = nfilename;
	} else {
	    free(nfilename);
	}
    }
#endif /* AFS_NT40_ENV */
    if (asprintf(&nfilename, "%s.NXX", filename) < 0) {
	code = -1;
	goto out;
    }
    tf = fopen(filename, "r");
    if (!tf) {
	code = -1;
	goto out;
    }
    code = stat(filename, &tstat);
    if (code < 0) {
	goto out;
    }
    nf = fopen(nfilename, "w+");
    if (!nf) {
	code = EIO;
	goto out;
    }
    flag = 0;
    found = 0;
    while (1) {
	/* check for our user id */
	tp = fgets(buffer, USERLIST_MAXLINESIZE, tf);
	if (tp == NULL)
	    break;
	if (strlen(buffer) > USERLIST_MAXLINESIZE - 2) {
	    code = ERANGE;
	    flag = 1;
	    break;
	}
	copy = strdup(buffer);
	if (copy == NULL) {
	    flag = 1;
	    break;
	}
	code = ParseLine(copy, &identity);
	if (code == 0 && rx_identity_match(user, &identity)) {
	    /* found the guy, don't copy to output file */
	    found = 1;
	} else {
	    /* otherwise copy original line to output */
	    fprintf(nf, "%s", buffer);
	}
	free(copy);
	rx_identity_freeContents(&identity);
    }
    if (ferror(nf))
	flag = 1;
    if (fclose(nf) == EOF)
	flag = 1;
    if (flag == 0) {
	/* try the rename */
	flag = rk_rename(nfilename, filename);
	if (flag == 0)
	    flag = chmod(filename, tstat.st_mode);
    } else
	unlink(nfilename);

    /* finally, decide what to return to the caller */
    if (flag)
	code = EIO;		/* something mysterious went wrong */
    else if (!found)
	code = ENOENT;		/* entry wasn't found, no changes made */
    else
	code = 0;		/* everything was fine */

  out:
    if (tf != NULL)
	fclose(tf);
    UNLOCK_GLOBAL_MUTEX;
    free(filename);
    free(nfilename);
    free(buffer);
    return code;
}

/*!
 * Remove a legacy Kerberos 4 name from the UserList file.
 *
 * This function removes a Kerberos 4 name from the super user list. It
 * can only remove names which were added by the afsconf_AddUser interface,
 * or with an explicit Kerberos v4 type.
 *
 * @param[in] adir
 * 	A structure representing the configuration directory
 * @param[in] name
 * 	The Kerberos v4 name to remove
 *
 * @returns
 * 	0 on success, an error code upon failure.
 *
 * Note that this function is deprecated. New callers should use
 * afsconf_DeleteIdentity instead.
 */

int
afsconf_DeleteUser(struct afsconf_dir *adir, char *name)
{
    struct rx_identity *user;
    int code;

    user = rx_identity_new(RX_ID_KRB4, name, name, strlen(name));
    if (!user)
	return ENOMEM;

    code = afsconf_DeleteIdentity(adir, user);

    rx_identity_free(&user);

    return code;
}

/* This is a multi-purpose funciton for use by either
 * GetNthIdentity or GetNthUser. The parameter 'id' indicates
 * whether we are counting all identities (if true), or just
 * ones which can be represented by the old-style interfaces
 * We return -1 for EOF, 0 for success, and >0 for all errors.
 */

int
afsconf_GetIdentity(struct afsconf_dir *dir,
		    struct rx_identity **identity,
		    int (*compare)(struct rx_identity *id, void *rock),
		    void *rock)
{
    int code;

    LOCK_GLOBAL_MUTEX;
    code = GetIdentity(dir, identity, compare, rock);
    UNLOCK_GLOBAL_MUTEX;
    return code;
}

static int
GetIdentity(struct afsconf_dir *dir,
	    struct rx_identity **identity,
	    int (*compare)(struct rx_identity *id, void *rock),
	    void *rock)
{
    bufio_p bp = NULL;
    char *filename = NULL;
    char *tbuffer = NULL;
    struct rx_identity fileUser;
    afs_int32 code;
    int found = 0;

    memset(&fileUser, 0, sizeof(fileUser));
    tbuffer = calloc(USERLIST_MAXLINESIZE, sizeof(*tbuffer));
    if (tbuffer == NULL) {
	code = ENOMEM;
	goto out;
    }

    code = asprintf(&filename, "%s/%s", dir->name, AFSDIR_ULIST_FILE);
    if (code < 0) {
	code = ENOMEM;
	goto out;
    }
    bp = BufioOpen(filename, O_RDONLY, 0);
    if (!bp) {
	code = -1;
	goto out;
    }
    while (1) {
	rx_identity_freeContents(&fileUser);
	code = BufioGets(bp, tbuffer, USERLIST_MAXLINESIZE);
	if (code < 0) {
	    code = -1;
	    break;
	}

	if (strlen(tbuffer) > USERLIST_MAXLINESIZE - 2) {
	    code = ERANGE;
	    break;
	}

	code = ParseLine(tbuffer, &fileUser);
	if (code != 0)
	    break;

	if (compare(&fileUser, rock)) {
	    *identity = rx_identity_copy(&fileUser);
	    if (*identity == NULL) {
		code = ENOMEM;
		break;
	    }
	    found = 1;
	    break;
	}
    }
    if (code == 0 && !found)
	code = ENOENT;

  out:
    if (bp)
	BufioClose(bp);
    rx_identity_freeContents(&fileUser);
    free(filename);
    free(tbuffer);
    return code;
}


/*!
 * Return the Nth super user identity from the UserList
 *
 * @param[in] dir
 * 	A structure representing the configuration directory
 * @param[in] count
 * 	A count (from zero) of the entries to return from the
 * 	UserList
 * @param[out] identity
 * 	A pointer to the Nth identity
 * @returns
 *      status code
 * @retval 0 Success
 * @retval -1 We have searched beyond the end of the list.
 * @retval >0 Error
 */
int
afsconf_GetNthIdentity(struct afsconf_dir *dir, int count,
		       struct rx_identity **identity)
{
   struct cursor cursor = {0, count};
   return afsconf_GetIdentity(dir, identity, id_at_index, &cursor);
}

/*!
 * Return the Nth Kerberos v4 identity from the UserList
 *
 * This returns the Nth old, kerberos v4 style name from
 * the UserList file. In counting entries it skips any other
 * name types it encounters - so will hide any new-style
 * identities from its callers.
 *
 * @param[in] dir
 * 	A structure representing the configuration directory
 * @param[in] count
 * 	A count (from zero) of the entries to return from the
 * 	UserList
 * @param abuffer
 * 	A string in which to write the name of the Nth identity
 * @param abufferLen
 * 	The length of the buffer passed in abuffer
 * @returns
 *      status code
 * @retval 0 Success
 * @retval 1 Either an EPERM error, or we have searched beyond the end of the
 *           list.
 * @retval >1 All other errors.
 *
 * This function is deprecated, all new callers should use
 * GetNthIdentity instead. This function is particularly dangerous
 * as it will hide any new-style identities from callers. It is also
 * impossible to distinguish an EPERM error from a normal end-of-file
 * condition with this function.
 */

int
afsconf_GetNthUser(struct afsconf_dir *adir, afs_int32 an, char *abuffer,
		   afs_int32 abufferLen)
{
    struct rx_identity *identity = NULL;
    int code;
    struct cursor cursor = {0, an};

    code = afsconf_GetIdentity(adir, &identity, user_at_index, &cursor);
    if (code == 0) {
	strlcpy(abuffer, identity->displayName, abufferLen);
    } else if (code == ENOENT) {
	code = 1; /* afsconf_GetNthUser() returns 1 to indicate EOF. */
    }
    rx_identity_free(&identity);
    return code;
}

/*!
 * Parse a UserList list
 *
 * Parse a line of data from a UserList file
 *
 * This parses a line of data in a UserList, and populates the passed
 * rx_identity structure with the information about the user.
 *
 * @param buffer	A string containing the line to be parsed
 * @param user		The user structure to be populated
 *
 * Note that the user->displayName, and user->exportedName.val fields
 * must be freed with free() by the caller.
 *
 * This function damages the buffer thats passed to it. Callers are
 * expected to make a copy if they want the buffer preserved.
 *
 * @return
 * 	0 on success, non-zero on failure.
 */

static int
ParseLine(char *buffer, struct rx_identity *user)
{
    char *ptr;
    char *ename;
    char *displayName;
    char *decodedName;
    int len;
    int kind;
    int code;

    /* Trim the trailing newline, if present. */
    ptr = strchr(buffer, '\n');
    if (ptr != NULL)
	*ptr = '\0';

    if (buffer[0] == ' ') { /* extended names have leading space */
	ptr = buffer + 1;
	code = sscanf(ptr, "%i", &kind);
	if (code != 1)
	    return EINVAL;

	strsep(&ptr, " "); /* skip the bit we just read with scanf */
	ename = strsep(&ptr, " "); /* Pull out the ename */
	displayName = strsep(&ptr, " "); /* Display name runs to the end */
	if (ename == NULL || displayName == NULL)
	    return EINVAL;

	decodedName = malloc(strlen(ename));
	if (decodedName == NULL)
	    return ENOMEM;

	len = base64_decode(ename, decodedName);
	if (len<0) {
	    free(decodedName);
	    return EINVAL;
	}

	rx_identity_populate(user, kind, displayName, decodedName, len);
	free(decodedName);

	return 0; /* Success ! */
    }

    /* No extended name. This is a legacy name. */
    rx_identity_populate(user, RX_ID_KRB4, buffer, buffer, strlen(buffer));
    return 0;
}

/*!
 * Check if a given identity is in the UserList file,
 * and thus is a super user
 *
 * @param adir
 * 	A structure representing the configuration directory to check
 * @param user
 * 	The identity to check
 * @returns
 * 	True if the user is listed in the UserList, otherwise false
 */
int
afsconf_IsSuperIdentity(struct afsconf_dir *adir,
			struct rx_identity *user)
{
    struct rx_identity *fileUser = NULL;
    int code;

    if (user->kind == RX_ID_SUPERUSER)
	return 1;

    code = GetIdentity(adir, &fileUser, id_matches, user);
    rx_identity_free(&fileUser);
    return (code == 0);
}

/* add a user to the user list, checking for duplicates */
int
afsconf_AddIdentity(struct afsconf_dir *adir, struct rx_identity *user)
{
    FILE *tf = NULL;
    afs_int32 code;
    char *ename = NULL;
    char *filename = NULL;
    char *buffer = NULL;
    size_t len;

    LOCK_GLOBAL_MUTEX;
    if (afsconf_IsSuperIdentity(adir, user)) {
	code = EEXIST;		/* already in the list */
	goto out;
    }

    code = asprintf(&filename, "%s/%s", adir->name, AFSDIR_ULIST_FILE);
    if (code < 0) {
	code = ENOMEM;
	goto out;
    }
    tf = fopen(filename, "a+");
    if (!tf) {
	code = EIO;
	goto out;
    }
    if (user->kind == RX_ID_KRB4) {
	/* Do not allow empty names and do not exceed the maximum supported
	 * line size. */
	len = strlen(user->displayName);
	if (len < 1 || len > USERLIST_MAXLINESIZE - 2) {
	    code = EINVAL;
	    goto out;
	}
	/* Do not allow newlines, since those are identity separators. */
	if (strcspn(user->displayName, "\r\n") != len) {
	    code = EINVAL;
	    goto out;
	}
	/* Do not allow the first char to be a space, since we use a space
	 * in the first position to indicates a new style identity. */
	if (user->displayName[0] == ' ') {
	    code = EINVAL;
	    goto out;
	}
	fprintf(tf, "%s\n", user->displayName);
    } else {
	base64_encode(user->exportedName.val, user->exportedName.len, &ename);
	code = asprintf(&buffer, " %d %s %s", user->kind, ename, user->displayName);
	if (code < 0) {
	    code = ENOMEM;
	    goto out;
	}
	len = strlen(buffer);
	/* Do not exceed the maximum supported line size. */
	if (len > USERLIST_MAXLINESIZE - 2) {
	    code = EINVAL;
	    goto out;
	}
	/* Do not allow newlines, since those are identity separators. */
	if (strcspn(buffer, "\r\n") != len) {
	    code = EINVAL;
	    goto out;
	}
	fprintf(tf, "%s\n", buffer);
    }
    code = 0;

  out:
    if (tf != NULL) {
	if (ferror(tf))
	    code = EIO;
	if (fclose(tf))
	    code = EIO;
    }
    free(buffer);
    free(filename);
    free(ename);
    UNLOCK_GLOBAL_MUTEX;
    return code;
}

int
afsconf_AddUser(struct afsconf_dir *adir, char *aname)
{
    struct rx_identity *user;
    int code;

    user = rx_identity_new(RX_ID_KRB4, aname, aname, strlen(aname));
    if (user == NULL)
	return ENOMEM;

    code = afsconf_AddIdentity(adir, user);

    rx_identity_free(&user);

    return code;
}

/* special CompFindUser routine that builds up a princ and then
	calls finduser on it. If found, returns char * to user string,
	otherwise returns NULL. The resulting string should be immediately
	copied to other storage prior to release of mutex. */
static int
CompFindUser(struct afsconf_dir *adir, char *name, char *sep, char *inst,
	     char *realm, struct rx_identity **identity)
{
    static char fullname[MAXKTCNAMELEN + MAXKTCNAMELEN + MAXKTCREALMLEN + 3];
    struct rx_identity *testId;

    /* always must have name */
    if (!name || !name[0]) {
	return 0;
    }

    if (strlcpy(fullname, name, sizeof(fullname)) >= sizeof(fullname))
	return 0;

    /* might have instance */
    if (inst && inst[0]) {
	if (!sep || !sep[0]) {
	    return 0;
	}

	if (strlcat(fullname, sep, sizeof(fullname)) >= sizeof(fullname))
	    return 0;

	if (strlcat(fullname, inst, sizeof(fullname)) >= sizeof(fullname))
	    return 0;
    }

    /* might have realm */
    if (realm && realm[0]) {
	if (strlcat(fullname, "@", sizeof(fullname)) >= sizeof(fullname))
	    return 0;

	if (strlcat(fullname, realm, sizeof(fullname)) >= sizeof(fullname))
	    return 0;
    }

    testId = rx_identity_new(RX_ID_KRB4, fullname, fullname, strlen(fullname));
    if (afsconf_IsSuperIdentity(adir, testId)) {
	if (identity)
	     *identity = testId;
	else
	     rx_identity_free(&testId);
	return 1;
    }

    rx_identity_free(&testId);
    return 0;
}

static int
kerberosSuperUser(struct afsconf_dir *adir, char *tname, char *tinst,
		  char *tcell, struct rx_identity **identity)
{
    char tcell_l[MAXKTCREALMLEN] = "";
    int code;
    afs_int32 islocal;
    int flag;

    /* generate lowercased version of cell name */
    if (tcell)
	opr_lcstring(tcell_l, tcell, sizeof(tcell_l));

    code = afsconf_IsLocalRealmMatch(adir, &islocal, tname, tinst, tcell);
    if (code) {
	return 0;
    }

    /* start with no authorization */
    flag = 0;

    /* localauth special case */
    if ((tinst == NULL || strlen(tinst) == 0) &&
	(tcell == NULL || strlen(tcell) == 0)
	&& !strcmp(tname, AUTH_SUPERUSER)) {
	if (identity)
	    *identity = rx_identity_new(RX_ID_KRB4, AFS_LOCALAUTH_NAME,
	                                AFS_LOCALAUTH_NAME, AFS_LOCALAUTH_LEN);
	flag = 1;

	/* cell of connection matches local cell or one of the realms */
    } else if (islocal) {
	if (CompFindUser(adir, tname, ".", tinst, NULL, identity)) {
	    flag = 1;
	}
	/* cell of conn doesn't match local cell or realm */
    } else {
	if (CompFindUser(adir, tname, ".", tinst, tcell, identity)) {
	    flag = 1;
	} else if (CompFindUser(adir, tname, ".", tinst, tcell_l, identity)) {
	    flag = 1;
	}
    }

    return flag;
}

static int
rxkadSuperUser(struct afsconf_dir *adir, struct rx_call *acall,
	       struct rx_identity **identity)
{
    char tname[MAXKTCNAMELEN];	/* authentication from ticket */
    char tinst[MAXKTCNAMELEN];
    char tcell[MAXKTCREALMLEN];

    afs_uint32 exp;
    int code;

    /* get auth details from server connection */
    code = rxkad_GetServerInfo(rx_ConnectionOf(acall), NULL, &exp, tname,
			       tinst, tcell, NULL);
    if (code)
	return 0;		/* bogus connection/other error */

    return kerberosSuperUser(adir, tname, tinst, tcell, identity);
}

#ifdef AFS_RXGK_ENV
static int
rxgkSuperUser(struct afsconf_dir *adir, struct rx_call *acall,
	      struct rx_identity **identity_out)
{
    struct rx_identity *identity = NULL;
    int is_super = 0;

    if (rxgk_GetServerInfo(rx_ConnectionOf(acall), NULL /*level*/, NULL /*expiry*/,
                           &identity) != 0)
        return 0;

    if (afsconf_IsSuperIdentity(adir, identity)) {
        is_super = 1;
        if (identity_out != NULL) {
            *identity_out = identity;
            identity = NULL;
        }
    }
    if (identity != NULL) {
        rx_identity_free(&identity);
    }
    return is_super;
}
#endif /* AFS_RXGK_ENV */

/*!
 * Check whether the user authenticated on a given RX call is a super
 * user or not. If they are, return a pointer to the identity of that
 * user.
 *
 * @param[in] adir
 * 	The configuration directory currently in use
 * @param[in] acall
 * 	The RX call whose authenticated identity is being checked
 * @param[out] identity
 * 	The RX identity of the user. Caller must free this structure.
 * @returns
 * 	True if the user is a super user, or if the server is running
 * 	in noauth mode. Otherwise, false.
 */
afs_int32
afsconf_SuperIdentity(struct afsconf_dir *adir, struct rx_call *acall,
		      struct rx_identity **identity)
{
    struct rx_connection *tconn;
    afs_int32 code;
    int flag;

    LOCK_GLOBAL_MUTEX;
    if (!adir) {
	code = 0;
	goto out;
    }

    if (afsconf_GetNoAuthFlag(adir)) {
	if (identity)
	    *identity = rx_identity_new(RX_ID_KRB4, AFS_NOAUTH_NAME,
	                                AFS_NOAUTH_NAME, AFS_NOAUTH_LEN);
	code = 1;
	goto out;
    }

    tconn = rx_ConnectionOf(acall);
    code = rx_SecurityClassOf(tconn);
    if (code == RX_SECIDX_NULL) {
	code = 0;		/* not authenticated at all, answer is no */
	goto out;
    } else if (code == RX_SECIDX_VAB) {
	/* bcrypt tokens */
	code = 0;		/* not supported any longer */
	goto out;
    } else if (code == RX_SECIDX_KAD) {
	flag = rxkadSuperUser(adir, acall, identity);
	code = flag;
	goto out;
#ifdef AFS_RXGK_ENV
    } else if (code == RX_SECIDX_GK) {
	flag = rxgkSuperUser(adir, acall, identity);
	code = flag;
	goto out;
#endif
    } else {			/* some other auth type */
	code = 0;		/* mysterious, just say no */
	goto out;
    }

  out:
    UNLOCK_GLOBAL_MUTEX;
    return code;
}

/*!
 * Check whether the user authenticated on a given RX call is a super
 * user or not. If they are, return a pointer to the name of that
 * user.
 *
 * @param[in] adir
 * 	The configuration directory currently in use
 * @param[in] acall
 * 	The RX call whose authenticated identity is being checked
 * @param[out] namep
 * 	A printable version of the name of the user
 * @returns
 * 	True if the user is a super user, or if the server is running
 * 	in noauth mode. Otherwise, false.
 *
 * This function is provided for backwards compatibility. New callers
 * should use the afsconf_SuperIdentity function.
 */

afs_int32
afsconf_SuperUser(struct afsconf_dir *adir, struct rx_call *acall,
		  char *namep)
{
    struct rx_identity *identity;
    int ret;

    if (namep) {
	ret = afsconf_SuperIdentity(adir, acall, &identity);
	if (ret) {
	    if (identity->kind == RX_ID_KRB4) {
		strlcpy(namep, identity->displayName, MAXKTCNAMELEN-1);
	    } else {
		snprintf(namep, MAXKTCNAMELEN-1, "eName: %s",
			 identity->displayName);
	    }
	    rx_identity_free(&identity);
	}
    } else {
	ret = afsconf_SuperIdentity(adir, acall, NULL);
    }

    return ret;
}

/*!
 * Check whether the user authenticated on a given RX call is
 * compatible with the access specified by needed_level.
 *
 * @param[in] adir
 * 	The configuration directory currently in use
 * @param[in] acall
 * 	The RX call whose authenticated identity is being checked
 * @param[in] needed_level
 * 	Either RESTRICTED_QUERY_ANYUSER for allowing any access or
 * 	RESTRICTED_QUERY_ADMIN for allowing super user only.
 * @returns
 * 	True if the user is compatible with needed_level.
 *      Otherwise, false.
 */

int
afsconf_CheckRestrictedQuery(struct afsconf_dir *adir,
			     struct rx_call *acall,
			     int needed_level)
{
    if (needed_level == RESTRICTED_QUERY_ANYUSER)
	return 1;

    return afsconf_SuperIdentity(adir, acall, NULL);
}
