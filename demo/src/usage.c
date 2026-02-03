/* Tests how past and present macros are presented in HTML.
 *
 * Macros can be:
 * Active - In scope at the end of processing a translation unit
 *   (one per identifier).
 * Inactive - Not in scope at the end of processing a translation unit
 *   (>=0 per identifier).
 * And:
 * Referenced - Have had some influence over the processing of the
 *   translation unit.
 * Not Referenced - No influence over the processing of the translation unit.
 */

/* Source         Active?    Refs    ID   */
#define FOO(a) 2*a    /*     N        0    FOO_0 */
#undef FOO
#define FOO(b) 2*b    /*     N        2    FOO_1 */
FOO(4)
#undef FOO
#define FOO    /*     Y        1    FOO_2 */
FOO
#define BAR    /*     Y        0    BAR_0 */
