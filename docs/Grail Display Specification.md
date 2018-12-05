# Grail display specification

Following document describes how Grail compatible display should work.

## How it works

> Display refers to any implementation of Grail Display compatible server.

Grail Display - is a simple media server. 
Display receive OSC messages and creating video output.

Display can be remote (separate application), and as Grail plugin (works in same process as Grail).

Display is a state machine, when message is received state must be saved.
Animation

## Media Server

> todo: add description of Media Server

## OSC Specification

### Data types

	int - OSC int
	str - OSC ASCII string
	bool - OSC boolean
	float - OSC float

> todo: add OSC types

### Display

Control display window

	display/width int
	display/height int
	display/x int
	display/y int
	display/fullscreen bool
	display/output str # name of display to output in fullscreen
	display/disabled bool

### Composition

Composition control

	comp/width int
	comp/height int
	comp/opacity float
	comp/transition float # seconds
	comp/volume float
	comp/pan float
	comp/testcard bool

### Clip

	clip/width float
	clip/height float
	clip/position float float
	clip/ratate float
	clip/opacity float
	clip/scale float
	clip/anchor float float float

	clip/audio/volume float
	clip/audio/pan float # -1 left, 1 right, 0 center

	clip/text/source str
	clip/text/color str
	clip/text/padding float float float float # left, top, right, bottom
	clip/text/align int # 0 - Left, 1 - Center, 2 - Right
	clip/text/valign int # 0 - Top, 1 - Center, 2 - Bottom
	clip/text/shadow/x int
	clip/text/shadow/y int
	clip/text/shadow/color str
	clip/text/shadow/blur int
	clip/text/transform int # 0 - Normal, 1 - Title, 2 - Upper, 3 - Lower, 4 - Capitalize
	clip/text/font/name
	clip/text/font/size
	clip/text/font/style

	clip/playback/source str
	clip/playback/direction bool # playback direction True for forward, False for backwards
	clip/playback/play
	clip/playback/pause
	clip/playback/stop
	clip/playback/transport int # 0 - loop, 1 - bounce, 2 - stop in the end, 3 - pause in the end
	clip/playback/start float # seocnds
	clip/playback/stop float # seconds
