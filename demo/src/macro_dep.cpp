#define NEW OLD

#define OLD 1

#if NEW > 1
Foo
#else
Bar
#endif

#undef OLD

#define OLD 2

#if NEW > 1
Foo
#else
Bar
#endif

#ifdef BAZ
Baz
#endif
