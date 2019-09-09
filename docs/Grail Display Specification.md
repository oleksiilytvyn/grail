# Grail OSC communication

This document explains how Grail OSC works.


## Grail display specification

Following document describes how Grail compatible display should work.

### How it works

> Display refers to any implementation of Grail Display compatible server.

Grail Display - is a simple media server. 
Display receive OSC messages and creating video output.

Display can be remote (separate application), and as Grail plugin (works in same process as Grail).

Display is a state machine, when message is received state must be saved.
Animation

### Media Server

Media is a program that can receive OSC messages from Grail and render video output.  
Below messages that Grail sends.

### OSC Specification

#### Data types

	int - OSC int
	str - OSC ASCII string
	bool - OSC boolean
	float - OSC float

#### Display

Configure render output window

	display/size <width:int> <height:int>
	display/pos <x:int> <y:int>
	display/fullscreen <flag:bool>
	display/output <display_name:str>
	display/disabled <flag:bool>


#### Composition

Virtual composition

	comp/size <width:int> <height:int>
	comp/opacity <opacity:float>
	comp/transition <seconds:float>
	comp/volume <level:float>
	comp/testcard <flag:bool>


#### Cue text

Cue Information, not used in rendering but may be used for debugging.

    cue/type <type:str>
    cue/name <name:str>
    cue/color <hex:str>
    cue/number <number:str>


#### Clip

Media Playback Control

Text control

	clip/text <text:str>
	clip/text/color <hex:str>
	clip/text/padding <left:float> <top:float> <right:float> <bottom:float>
	clip/text/align <horizontal:str values("left", "center", "right")> <vertical:str values("top", "middle", "bottom")>
	clip/text/shadow <x:int> <y:int> <blurinness:int> <hex:str>
	clip/text/transform <type:str values("normal", "title", "upper", "lower", "capitalize")>
	clip/text/font <size_pt:float> <family:str> <style:str>

Clip control, <N> is number of clip layer starting from 1

	clip/<N>/size <width:int> <height:int>
	clip/<N>/pos <x:float> <y:float>
	clip/<N>/rotate <angle:float>
	clip/<N>/opacity <opacity:float>
	clip/<N>/volume <value:float>
	clip/<N>/scale <scale:float>

	clip/<N>/playback/source <path:str>
	clip/<N>/playback/play
	clip/<N>/playback/pause
	clip/<N>/playback/stop
	clip/<N>/playback/position <position:float>
	clip/<N>/playback/transport <type:str values("loop", "stop", "pause")>
