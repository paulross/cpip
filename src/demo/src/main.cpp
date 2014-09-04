#include "user.h"

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
