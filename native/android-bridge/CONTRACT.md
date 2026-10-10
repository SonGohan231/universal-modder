# Transport contract v1

Scope: state/event transport only, not engine integration. Closest repository
example: minecraft-gta5-passthrough; Windows process APIs replaced by POSIX sockets.

The host creates an AF_UNIX SOCK_SEQPACKET socketpair, authenticates/cooperatively
hands off the endpoints, and assigns a nonzero epoch. The transport never discovers
or attaches to an installed app. Each endpoint has one sending and one receiving
owner; callers must serialize concurrent access. No raw pointers cross the boundary.

48-byte little-endian packet (explicit byte encoding, no C++ struct layout on wire):
magic 0x31464d55, version=1, epoch, sequence, tick, entity ID, entity generation,
x_milli, y_milli, value, kind, reserved=0; every field is 32 bits.
x/y/value are signed. Kind: spawn=1, position=2, damage=3, pause=4, resume=5.
Coordinates are integer millunits in a caller-defined world, x right/y up.
No mapping to either game's world is established yet.

Sequence advances only on successful send; duplicates/out-of-order messages and
wrong epochs are rejected. Overflow requires a new connection/epoch. No automatic
replay or retry; FULL means caller must retry discrete events or explicitly coalesce
position updates. Kernel socket queues bound memory. Calls never wait for a peer.
Pause discards gameplay messages until resume. Tick is metadata, not a scheduler;
no latency/freshness watchdog is implemented. On disconnect the owner must stop
advancing dependent gameplay and reconnect with a fresh pair/epoch.

No combat, camera, rendering, saves or inventory authority is implemented. The host
must define it before wiring engine callbacks. Session test uses fork within Termux;
it does not establish cross-package SELinux/permission access.
