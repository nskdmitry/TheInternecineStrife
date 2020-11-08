class Age:
  Neolit = 0
  Bronze = 1
  Iron = 2
  Middle = 3
  Industrial = 4

class Environments:
    Air = 0
    Earth = 1
    Water = 2
    Bridge = 3
    Port = 4

    # 0.0 is eq of "Without energy leeks"
    FLY = 0.0
    # 1000.0 is eq of "Not move"
    IMPOSSIBLE = 1000.0

    # Air -> Air, Earth, Water, Bridge, Port
    # Earth -> Air, Earth, Water, Bridge, Port
    # Water -> Air, Earth, Water, Bridge, Port
    # Bridge -> Air, Earth, Water, Bridge, Port
    # Port -> Air, Earth, Water, Bridge, Port
    Cost = [[FLY, IMPOSSIBLE, IMPOSSIBLE, 1.0, IMPOSSIBLE]
        , [IMPOSSIBLE, 0.1, IMPOSSIBLE, 0.4, 0.3]
        , [IMPOSSIBLE, IMPOSSIBLE, 0.1, 0.75, 0.5]
        , [IMPOSSIBLE, 0.4, IMPOSSIBLE, 0.4, 0.4]
        , [IMPOSSIBLE, 0.3, 0.4, 0.3, 0.3]
    ]

class Orientation:
    Tax = 0
    Food = 1
    Source = 2
    Weapon = 3
    Recruit = 4
    Progress = 5
