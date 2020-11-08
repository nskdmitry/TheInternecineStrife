--- Sqlite3 initial DB script.

/*
  Statuses - state of player/lord or game.

  toSkip - if toSkip > 0 then skip lord on game circle or skip game at select available games.
  both - this status can be set for player/lord and game both.
*/
CREATE TABLE statuses (
  id INTEGER PRIMARY KEY ASC,
  name TEXT,
  toSkip INTEGER DEFAULT 0,
  both INTEGER DEFAULT 1
);
/*
  Game on server.
  # Started - timestamp of game created and started;
  # Ended - finish timestamp of game as timestamp;
  # playersLimit - maximal count of players (with AI but without player by default);
  # face - length of side of map (width and height);
  # level - filter of codexes, terrain types, resources and et cetra;
  # store - path to file of main save of this game.
*/
CREATE TABLE games (
  id INTEGER PRIMARY KEY ASC,
  name TEXT,
  started INTEGER,
  finished integer,
  playersLimit integer,
  face integer,
  level integer,
  status INTEGER DEFAULT 1,
  store text
);
/*
  AI is computer opponent and player's deputer. Player can set AI instead of heself/herself.
  # level - How many capabilites of game mechanic AI can uses?
  # online - Deputer (AI) is run as web daemon or as class in the game scope?
  # server, port - Parameters of TCP/WebSocket connection to online AI daemon.
*/
CREATE TABLE ai (
  id INTEGER PRIMARY KEY ASC,
  name text,
  level INTEGER DEFAULT 1,
  online INTEGER DEFAULT 0,
  server text,
  port INTEGER
);
/*
  User of game.
  # hash = sha256(login + password + salt) + sha256(password + salt)
*/
CREATE TABLE players (
  id INTEGER PRIMARY KEY ASC,
  login text,
  hash text,
  registeredAt INTEGER,
  ip TEXT,
  port integer
);
/*
  Lords is avatr of player in the concretical game. Relative to game and statistics.
  # Deputer - Deputer is AI what will play instead of this player if player has 'deputed' status.
*/
CREATE TABLE lords (
  id INTEGER PRIMARY KEY ASC,
  name text,
  idGame integer DEFAULT 0,
  status INTEGER DEFAULT 1,
  deputer INTEGER DEFAULT 0,
  idPlayer INTEGER,
  startedGold REAL
);

CREATE TABLE goods (
  id INTEGER PRIMARY KEY,
  name TEXT,
  cost REAL
);

CREATE TABLE SaleStatus (
  id INTEGER PRIMARY KEY,
  name TEXT,
  finally INTEGER DEFAULT 0
);
INSERT INTO SaleStatus VALUES (1, 'await'), (2, 'sent'), (3, 'closed', 1), (4, 'completed', 1);

-- Statistics and game-session information

-- Log-in and log-out of players
/*
  # at - timestamp of audit activity.
  # If logIn == 0 then user-player finish game session.
  # sessionHash - digest of current player session = sha256(user.login + user.hash + date(audit.at) + date(audit.expire) + salt). Use to sign a requests.
  # expire - timestamp when user or client application must be confirm connection.
  # idGame > 0 if event is in/out game event.
*/
CREATE TABLE audit (
  id INTEGER PRIMARY KEY,
  idPlayer INTEGER,
  logIn INTEGER DEFAULT 1,
  at INTEGER,
  sessionHash TEXT,
  expire INTEGER,
  idGame INTEGER DEFAULT 0
);
-- Supply, demand and merchant deals
/*
  # toSale == 0 then it is _demand_ of goods to buy else is _supply_ to sale.
  # limitPrice - maximal price of buy or minimal price of sale.
  # timeCircle - no of game circle when was a created or last updated.
  # status - id of SaleStatus record.
*/
CREATE TABLE supply (id INTEGER PRIMARY KEY, idGame INTEGER, idCell INTEGER, limitPrice REAL, toSale INTEGER DEFAULT 0, timeCircle INTEGER, status INTEGER);
CREATE TABLE supplyItem (idSupply INTEGER, idGood INTEGER, count REAL);
CREATE TABLE deal (id INTEGER PRIMARY KEY, idSupply INTEGER, idDemand INTEGER, timeCircle INTEGER, status INTEGER);
