# Why a dumb tracker?

The purpose of a "dumb" tracker is to offer a more primitive tracking
object that allows for better data analysis, since it keeps track of a list
of coordinates rather than a list of arrival times at stops, which may not be
as accurate as a bus can be sitting in traffic for a while before it actually
gets to a stop and begins picking up passengers.

This also means that there will need to be suitable logic to ensure the right
"arrival time" is picked, as the time the bus is closest to the stop may not be
the time when it begins picking up or dropping off passengers.

A dumb tracker will also allows updates every second, as there will be minimal
processing needed.