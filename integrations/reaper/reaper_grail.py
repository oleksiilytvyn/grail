"""
  reaper.grail
  ~~~~~~~~~~~~

  Send Notes as OSC messages to grail display

  WARNING! Notes will be taken from selected track
"""
from reaper_python import *
from osc import *

# todo: Add GUI for selecting track and displaying lyrics

PORT = 8001
HOST = '192.168.1.15'
NOTES = ""
TRACK = None

client = OSCClient(HOST, PORT)

def ULT_GetMediaItemNote(p0):
  """Returns MediaItem notes"""

  a = rpr_getfp('ULT_GetMediaItemNote')
  f = CFUNCTYPE(c_char_p,c_uint64)(a)
  t = (rpr_packp('MediaItem*',p0),)
  r = f(t[0])
  return str(r.decode())

def selected_track():
  """returns first selected track"""

  track_sel = RPR_GetSelectedTrack(0, 0)

  return track_sel

def selected_track_name():
  """returns first selected track name"""

  val, track, track_name, buf_sz = RPR_GetTrackName(selected_track(), "", 20)

  return track_name

def loop():
  global NOTES, TRACK, client

  item_notes = ""
  state = RPR_GetPlayState()
  position = RPR_GetPlayPosition()

  track = TRACK
  count_items_on_track = RPR_CountTrackMediaItems(track)

  if not track:
    RPR_runloop("loop()")
    return False

  for i in range(count_items_on_track):
    item = RPR_GetTrackMediaItem(track, i)
    item_pos = RPR_GetMediaItemInfo_Value(item, "D_POSITION")
    item_len = RPR_GetMediaItemInfo_Value(item, "D_LENGTH")
    item_end = item_pos + item_len

    if position > item_pos and position < item_end:
      item_notes = ULT_GetMediaItemNote(item)
      break

  if item_notes != NOTES:
    NOTES = item_notes

    if len(item_notes) < 1:
      item_notes = " "

    msg = OSCMessage(address="/grail/message")
    msg.add(bytes(item_notes, "utf-8"))
    msg.add(0)

    client.send(msg)

    RPR_ShowConsoleMsg("")
    RPR_ShowConsoleMsg("\n" + item_notes)

  RPR_runloop("loop()")


TRACK = selected_track()

RPR_runloop("loop()")
