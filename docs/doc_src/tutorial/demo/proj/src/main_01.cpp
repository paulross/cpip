

#include "user.h"

/* Some functon */
#define FUNC(x,y,z) x ## y + z

#undef FRENCH
#define FRENCH 42
#undef FRENCH
#define FRENCH 78


int main(char **argv, int argc)
{
#if defined(LANG_SUPPORT) && defined(FRENCH)
    printf("Bonjour tout le monde\n");
#elif defined(LANG_SUPPORT) && defined(AUSTRALIAN)
    printf("Wotcha\n");
#else
    printf("Hello world\n");
#endif
    return 1;
}
