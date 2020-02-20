#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void *
crash(void)
{
    *(char *)1 = 'a';  /* Raises SIGSEGV */
    return NULL;       /* Unreachable */
}

int
main(int argc, char *argv[])
{
    printf("hello world\n");

    printf("zzz...\n");
    sleep(10);

    if (argc > 1 && strcmp(argv[1], "-crash") == 0) {
	printf("good bye\n");
	crash();
    }

    return 0;
}
