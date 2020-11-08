import sqlite3
import hashlib
import os
import re

storePath = os.path.dirname(__file__)
store = os.path.join(storePath, 'fw.sqlite')
if os.path.exists(store):
    os.remove(store)
connect = sqlite3.connect(store)
c = connect.cursor()

with file(os.path.join(storePath, 'init_db.sql'), 'r') as scriptWrite:
    script = scriptWrite.read()

c.executescript(script)

# Available: game is created but wait a players to start; player is not select game to play.
# On-line: game/player is play already.
# Off-line: game is paused and not wait a new players; player is select a game to play but not play (paused or connect is broken).
# Closed: game is finished; player is lost and cannot continue this game.
# Deputed: selected by player AI play instead of this player.
stats = [(1, 'Available', 0, 1), (2, 'Online', 0, 1), (3, 'Deputed', 0, 0), (4, 'Closed', 1, 1), (5, 'Offline', 1, 1)]
c.executemany("INSERT INTO statuses VALUES (?, ?, ?, ?)", stats)
