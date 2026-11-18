from collections import defaultdict
def run(rad_loss, fmt=0.9, label=""):
    need=defaultdict(float)   # intermediates / raws consumed
    by=defaultdict(float)     # by-products returned
    def add(d,k,v): d[k]+=v
    def coolant_makeup(units):
        add(need,'heavy-oil',2*units); gel(0.5*units)
        add(need,'copper-plate',0.2*units); add(need,'iron-plate',0.1*units); add(need,'sulfur',0.1*units)
    def gel(u):  # 20 gel = 10 space water + 100 PG
        spacewater(0.5*u); add(need,'petroleum-gas',5*u)
    def spacewater(u): # 10 = 99 water + 1 lube
        add(need,'water',9.9*u); add(need,'lubricant',0.1*u)
    def plasma(u): # 100 = 1 stone + 10 gel
        add(need,'stone',u/100); gel(u/10)
    def sand(u): add(need,'stone',u/3)
    def glass(u): sand(4*u)
    def supercooled(u):  # non-cryonite loop: each supercooled unit circulates 6 hot through radiators
        coolant_makeup(6*u*rad_loss)
    def cold(u, returns_hot=True):
        coolant_makeup(2*u*rad_loss)
    def contaminated_scrap(u):
        spacewater(0.1*u*(1-0.5*0.99)); scrap(u)
    def scrap(u):
        for k in('iron-ore','copper-ore','stone','heavy-oil'): add(by,k,0.1*u)
    def junk(u):  # formatting: fmt empty, 0.09 broken -> 5 scrap
        empty(-fmt*u); scrap(5*0.09*u)
    def empty(u):
        add(need,'advanced-circuit',3*u); add(need,'copper-plate',6*u)
        # 4 cleaned substrate: 2 glass + 4 iron plate each, 5 space water (99% recovered)
        glass(8*u); add(need,'iron-plate',16*u); spacewater(20*u*0.01)
        if u>0: scrap(4*0.5*u)
    def mirror(u):
        glass(6*u); add(need,'steel-plate',3*u); add(need,'low-density-structure',u); add(need,'se-heat-shielding',u)
        add(need,'lubricant',10*u); gel(u); scrap(u)
    def holmium_cable(u):
        plate=u; add(need,'plastic-bar',u/2)
        ingot=plate/10; sand(2*ingot); powder=50*ingot; add(need,'se-pyroflux',10*ingot)
        chloride=powder/2; add(need,'copper-cable',powder/10)
        add(need,'se-holmium-ore',4*chloride); add(by,'stone',0.25*2*chloride); add(need,'water',8*chloride)
        beads=2*chloride; rods=beads/10
        add(need,'se-cryonite',10*rods); add(need,'heavy-oil',rods); add(need,'plastic-bar',rods); add(need,'sulfuric-acid',5*rods)
    def fusion_card(u):
        add(need,'iron-plate',0.5*u); plasma(50*u)   # 50 proton stream
        ff=2*u                                       # forcefield crafts (50% success)
        supercooled(10*ff); holmium_cable(4*ff); empty(-ff); junk(0.49*ff); contaminated_scrap(ff)
        pol=ff/9                                     # polarisation crafts
        empty(10*pol); mirror(2*pol); cold(10*pol); junk(pol); scrap(2*pol)
        emf=ff/0.95
        empty(emf); add(need,'copper-plate',0.5*emf); plasma(50*emf); cold(10*emf); junk(0.04*emf)
        junk(u)                                      # the card itself ends life as junk data
    # ---- one matter-fusion-iron craft ----
    main=defaultdict(float)
    # particle stream 50 = 1/4 craft
    add(need,'iron-plate',.25); add(need,'copper-plate',.25); add(need,'stone',.25); add(need,'plastic-bar',.25)
    sand(1.25); plasma(25)
    supercooled(25)
    contaminated_scrap(1)
    snap={k:v for k,v in need.items()}
    fusion_card(0.01)
    card={k:need[k]-snap.get(k,0) for k in need if abs(need[k]-snap.get(k,0))>1e-12}
    print(f"\n===== {label} (radiator loss {rad_loss*100:g}%) =====")
    print("main path (no card):"); [print(f"   {k:24s}{v:9.4f}") for k,v in sorted(snap.items())]
    print("card upkeep (0.01 card):"); [print(f"   {k:24s}{v:9.5f}") for k,v in sorted(card.items())]
    print("by-products:"); [print(f"   {k:24s}{v:9.4f}") for k,v in sorted(by.items())]
    # raw reduction with ASSUMED vanilla recipes
    raw=defaultdict(float)
    conv={'iron-plate':{'iron-ore':1},'copper-plate':{'copper-ore':1},'copper-cable':{'copper-ore':.5},
          'plastic-bar':{'coal':.5,'petroleum-gas':10},'sulfur':{'petroleum-gas':15,'water':15},
          'lubricant':{'heavy-oil':1},'steel-plate':{'iron-ore':5},
          'sulfuric-acid':{'iron-ore':.02,'petroleum-gas':1.5,'water':3.5}}
    left=defaultdict(float)
    def red(k,v):
        if k in conv:
            for k2,m in conv[k].items(): red(k2,v*m)
        else: raw[k]+=v
    for k,v in need.items(): red(k,v)
    print("RAW (plates 1:1 ore, vanilla oil recipes assumed):"); [print(f"   {k:24s}{v:9.4f}") for k,v in sorted(raw.items())]
for r,l in((0.02,'standard'),(0.002,'slow'),(0.1,'fast')): run(r,label=l)
