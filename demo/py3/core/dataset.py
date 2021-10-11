import core.battle as battle
import core.world as world

weapons = []
weapons.append(battle.Weapon(name="stones", damage=1, typeRange=battle.Attack.RANGE, price={"gold": 0}, d=8)) #0
weapons.append(battle.Weapon(name="stone", damage=1, typeRange=battle.Attack.MALEE, price={"gold": 0}, d=0)) #1
weapons.append(battle.Weapon(name="woodspear", damage=3, typeRange=battle.Attack.MALEE, price={"gold": 0.2}, d=2, resource=100)) #2
weapons.append(battle.Weapon(name="stonespear", damage=4, typeRange=battle.Attack.MALEE, price={"gold": 0.3}, d=2, resource=100)) #3
weapons.append(battle.Weapon(name="stonedart", damage=4, typeRange=battle.Attack.RANGE, price={"gold": 0.3}, d=12, resource=3)) #4
weapons.append(battle.Weapon(name="bronzespear", damage=6, typeRange=battle.Attack.MALEE, price={"gold": 0.75}, d=3, resource=100)) #5
weapons.append(battle.Weapon(name="bronzepike", damage=6, typeRange=battle.Attack.MALEE, price={"gold": 1.0}, d=4, resource=100)) #6
weapons.append(battle.Weapon(name="bronzedart", damage=5, typeRange=battle.Attack.RANGE, price={"gold": 0.75}, d=12, resource=3)) #7
weapons.append(battle.Weapon(name="sarisse", damage=6, typeRange=battle.Attack.MALEE, price={"gold": 1.2}, d=5, resource=100)) #8
weapons.append(battle.Weapon(name="bronzesword", damage=8, typeRange=battle.Attack.MALEE, price={"gold": 6.2}, d=1)) #9
weapons.append(battle.Weapon(name="spata", damage=8, typeRange=battle.Attack.MALEE, price={"gold": 5.0}, d=1, resource=300))
weapons.append(battle.Weapon(name="bow", damage=3, typeRange=battle.Attack.RANGE, price={"gold": 2.0}, d=200, resource=20))
weapons.append(battle.Weapon(name="combobow", damage=4, typeRange=battle.Attack.RANGE, price={"gold": 5.0}, d=300, resource=20))
weapons.append(battle.Weapon(name="longbow", damage=3, typeRange=battle.Attack.RANGE, price={"gold": 2.2}, d=210, resource=20))

shields = []
shields.append(battle.Shield(name="wickedshield", squer=0.9, resource=5))  #0
shields.append(battle.Shield(name="skeenshield", squer=0.7, resource=20))  #1
shields.append(battle.Shield(name="armshield", squer=0.1, resource=100))   #2
shields.append(battle.Shield(name="bronzeshield", squer=0.4, resource=250))#3
shields.append(battle.Shield(name="woodshield", squer=0.4, resource=100))  #4
shields.append(battle.Shield(name="steelshield", squer=0.4, resource=300)) #5
shields.append(battle.Shield(name="dropshield", squer=0.7, resource=300))  #6

shields.append(battle.Shield(name="armoredbra", squer=0.02, resource=10))   #-1

formations = []
formations.append(battle.Sparse()) # 0
formations.append(battle.Wawes())  # 1
formations.append(battle.Persian()) # 2
formations.append(battle.Squer())   # 3
formations.append(battle.Phalanx()) # 4
formations.append(battle.LinedPhalanx()) # 5
formations.append(battle.Tortue()) # 6
formations.append(battle.Wedge()) # 7

warriors = []
warriors.append(battle.SoldierProfile(name="minitman", weapon=weapons[3], firetool=None, shield=shields[2], transport=battle.Transport.LEG, resource=1))
warriors.append(battle.SoldierProfile(name="darter", weapon=weapons[2], firetool=weapons[7], shield=shields[1], transport=battle.Transport.LEG, resource=3))
warriors.append(battle.SoldierProfile(name="archer", weapon=weapons[1], firetool=weapons[11], shield=shields[0], transport=battle.Transport.LEG, resource=20))
warriors.append(battle.SoldierProfile(name="pikeneer", weapon=weapons[6], firetool=None, shield=shields[5], transport=battle.Transport.LEG))
warriors.append(battle.SoldierProfile(name="nobelminitman", weapon=weapons[9], firetool=None, shield=shields[4], transport=battle.Transport.LEG))
warriors.append(battle.SoldierProfile(name="wagone", weapon=weapons[5], firetool=weapons[11], shield=shields[3], transport=battle.Transport.WAGONE, resource=30))
warriors.append(battle.SoldierProfile(name="lightcavalry", weapon=weapons[3], firetool=weapons[12], shield=shields[2], transport=battle.Transport.HORSE, resource=10))
warriors.append(battle.SoldierProfile(name="lightcavalry", weapon=weapons[5], firetool=weapons[7], shield=shields[2], transport=battle.Transport.HORSE, resource=3))
warriors.append(battle.SoldierProfile(name="hettairas", weapon=weapons[8], firetool=None, shield=shields[3], transport=battle.Transport.HORSE))
warriors.append(battle.SoldierProfile(name="mumbhoo", weapon=weapons[3], firetool=None, shield=shields[0], transport=battle.Transport.LEG))

warriors.append(battle.SoldierProfile(name="amazones", weapon=weapons[3], firetool=None, shield=shields[-1], transport=battle.Transport.LEG, resource=4)) # firetool=weapons[4]

mashines = []
mashines.append(battle.SeigeMachine(name="ram", distance=2, crashValue=30, corpus=shields[0], resource=200, sequence=1))
mashines.append(battle.SeigeMachine(name="woodram", distance=2, crashValue=30, corpus=shields[4], resource=200, sequence=1))
mashines.append(battle.SeigeMachine(name="anticram", distance=2, crashValue=40, corpus=shields[3], resource=220, sequence=1))
mashines.append(battle.SeigeMachine(name="scorpio", distance=200, crashValue=12, corpus=shields[2], resource=10, sequence=0.75))
mashines.append(battle.SeigeMachine(name="onager", distance=100, crashValue=20, corpus=shields[2], resource=60, sequence=3))

landscapes = []
landscapes.append(world.Landscape(name="doll", cross=0.1))
landscapes.append(world.Landscape(name="hills", cross=0.4))
landscapes.append(world.Landscape(name="mounts", cross=0.8))
landscapes.append(world.Landscape(name="forest", cross=0.6))
