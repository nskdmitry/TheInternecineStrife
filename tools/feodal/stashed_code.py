import operator

    # Layer 2: Castles of player.
    # Method: Random throw distances
    def genCastles(self, landscape, highmap, playerIDs=[0,1]):
        """
        Layer #2 - Castles (users bases, capitals of regions)
        IN: id[] landscape - id of landscape types
            float[] highmap - height of center of cell
            id[] playerIDs - id of Lords
        OUT: dict<cell.id, player.id> - id of player who have a castle in this cell or -1 (not-castle cell)
        """
        logging.debug("Stage Capitals layer")
        playersLimit = len(self.bases)
        self.players = min([playersLimit, len(playerIDs)])
        if self.players < 1:
            self.players = len(playerIDs)

        building = self.buildings[1]
        # Capitals of user manors
        def buider(no):
            return self.buildCastle(no, playerIDs.index(no), self.bases[no], landscape, highmap)
        castles = {self.bases[no]: buider(no) for no in playerIDs}
        self.domains = [self.domain(i + 1, self.bases[i], playerIDs[i]) for i in range(0, self.players)]

        # Free capitals of free regions
        amount = self.regions if self.regions != None else len(castles) + self.face + 1
        itercount = 0
        cap = len(castles) + 1
        while cap <= self.regions:
            placeId = self.rand.randint(0, self.size-1)
            # No reset exists capital
            if placeId in self.bases:
                logging.debug("  Cell {} is capital already".format(placeId))
                itercount = itercount + 1
                continue
            if castles.has_key(placeId):
                logging.debug("  Cell {} is capital already".format(placeId))
                itercount = itercount + 1
                continue

            # Variousity of capital building in this place. Time influences for it.
            remote = [ self.calcKoolonInfluence(1, 1, self.dd(placeId, capitalId), koeff=3) for capitalId in castles]
            remoteness = min(remote)
            # Remoteness between already set castles
            trakes = [ self.dd(capital1, capital2) for capital1 in castles for capital2 in castles if capital1 != capital2 ]
            relation = min(trakes)
            # Circle breaker
            timeCorrection = itercount / self.size
            # Building
            if relation - remoteness > timeCorrection:
                self.domains.append(self.domain(cap, placeId))
                castles[placeId] = cap
                landscape[placeId] = building
                cap = cap + 1
            itercount = itercount + 1

        return castles

    # Layer 5: Domains
    # Methods: Near of castles
    def genDomains(self, peasants, armies, castles, landscape):
        """
        Layer #5 - Domains (regions, countries, manors)
        IN: int[] peasants - population of cells,
            int[] armies - forces of cells,
            dict<cell.id, player.id> castles - capitals of regions
            id[] landscape - list of id of landcape in cells
        OUT: id[] - identifiers of cell's domain
        """
        logging.debug("Stage Domain's layer")
        # Collect a macro domains
        capitals = [cell for cell in castles.keys() if cell > -1]
        dd = self.dd

        def relation(idCell, idCapital):
            return self.calcKoolonInfluence(1, 1, dd(idCell, idCapital))

        def setDomain(idCell):
            nearing = [relation(idCell, capitalId) for capitalId in capitals]
            nearestNo = nearing.index(max(nearing))
            idDomain = castles[capitals[nearestNo]]
            return idDomain

        domains = [setDomain(i) for i in range(0, len(peasants))]
        return domains


    # Layer 5: Domains
    # Methods: Spreading from settled cells
    def genDomains(self, peasants, armies, castles, landscape):
        """
        Layer #5 - Domains (regions, countries, manors)
        IN: int[] peasants - population of cells,
            int[] armies - forces of cells,
            dict<cell.id, player.id> castles - capitals of regions
            id[] landscape - list of id of landcape in cells
        OUT: id[] - identifiers of cell's domain
        """
        logging.debug("Stage Domain's layer")
        capitals = [cell for cell in castles.keys() if cell > -1]
        # Stage 1: primary land development (many-many little regions)
        domainsList, domainsMap = self.genLandDevelopmentRegions(peasants)

        # Is stage of absorbation little regions need?
        if self.regionsIsConst == None or self.regionsIsConst == False:
            self.domains = domainsList
            return domainsMap

        # Stage 2: integration process (count of region come down to self.regions)
        domainsList, domainsMap = integrationRegions(peasants, castles, domainsList, domainsMap)

        self.domains = domainsList
        return domainsMap

    # Collect regios from more hobbitable cells to less hobbitable (resettlement)
    def genLandDevelopmentRegions(self, peasants):
        domainsList = [self.domain(0, -15, 0)]
        domainsMap = [0 for i in range(0, self.size)]

        # Sort by descending a population
        spreadingCenters = sorted([idCell for idCell in range(0, self.size)], key=lambda idCell: -peasants[idCell])
        for idCell in spreadingCenters:
            idDomain = domainsMap[idCell]
            # Create new region with center in current cell
            if idDomain == 0:
                domain = self.domain(len(domainsList), idCell, 0)
                domainsList.append(domain)
                idDomain = domain['id']
                domainsMap[idCell] = idDomain
            # Development nearest cells
            conquestions = [ cell for cell in self.getVecine(idCell) if domainsMap[cell] == 0 or peasants[cell] < peasants[idCell] ]
            for target in conquestions:
                domainsMap[target] = idDomain
        return (domainsList, domainsMap)

    # Integration a has not one of castle domains into castle holder's domains
    def integrationRegions(self, peasants, castles, domainsList, domainsMap):
        # Fix a capitals of domains
        greatCapitals = castles.keys()
        for castleCell in greatCapitals:
            idDomain = domainsMap[castleCell]
            domainsList[idDomain]['capital'] = castleCell

        # What a cells we will integrate?
        def toAbsorb(idCell):
            idNativeDomain = domainsMap[idCell]
            idCapitalCell = domainsList[idDomain]['capital']
            return not idCapitalCell in greatCapitals
        def absorbable(idDomain):
            return

        # Sort by ascending a population
        absorbing = sorted([idCell for idCell in range(0, self.size) if toAbsorb(idCell), key=lambda idCell: peasants[idCell])
        willAbsorb = {idDomain: len([idCell for idCell in absorbing if domainsMap[idCell] == idDomain]) for idDomain in domainsList if not domainsList[idDomain] in greatCapitals}

        # Absorbation of "ownerless" cells:
        while len(absorbing) > 0:
            for idCell in absorbing:
                # Already absorbed
                if not willAbsorb.has_key(domainsMap[idCell]):
                    absorbing.remove(idCell)
                    continue
                idNativeDomain = domainsMap[idCell]

                # Who will capture this cell?
                nearbores = self.getVecine(idCell, conv=lambda cell: domainsMap[cell])
                tirans = {idDomain: len([domain for domain in nearbores if domain == idDomain]) for idDomain in nearbores if idDomain != idNativeDomain and not willAbsorb.has_key(idDomain)}
                # Cell has not agressive neibors who can capture it.
                if len(tirans.iterkeys()) == 0:
                    logging.debug("Cell #{} is not has danger")
                    continue
                dominantPlaces = max(tirans.iteritems())
                idCapturer = self.getKey(tirans, dominantPlaces)
                if idCapturer == None:
                    logging.debug("Cell #{} is not has danger")
                    continue

                domainsMap[idCell] = idCapturer
                absorbing.remove(idCell)
                willAbsorb[idNativeDomain] = willAbsorb[idNativeDomain] - 1
                if willAbsorb[idNativeDomain] == 0:
                    willAbsorb.pop(idNativeDomain)
        return (domainsList, domainsMap)
