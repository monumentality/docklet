#ifdef DEBUG_CONNECTION
// Update the following if needed…
#define DEBUGC(ARGS...) printf(ARGS)
#else
#define DEBUGC(ARGS...) do {} while (0)
#endif

#ifdef DEBUG_ACO
// Update the following if needed…
#define DEBUGA(ARGS...) printf(ARGS)
#else
#define DEBUGA(ARGS...) do {} while (0)
#endif

#ifdef INFOMODE
// Update the following if needed…
#define INFO(ARGS...) printf(ARGS)
#else
#define INFO(ARGS...) do {} while (0)
#endif
