import state_init
import argparse

cursor = state_init.c

class Merchant:
    def __init__(self, cursor, idGame, idCell, time):
        self.cursor = cursor
        self.game = idGame
        self.time = time
        self.marketplace = idCell

        self.deals = []
        self.getTrades()

    def getTrades(self):
        self.cursor.execute("SELECT supply.* FROM supply INNER JOIN SaleStatus ON SaleStatus.id = supply.status WHERE idGame = ? AND finally < 1")
        self.trades = self.cursor.fetchall()
        self.requires = [trade for trade in self.trades if trade['idCell'] == self.marketplace]
        return self.trades

    def cupireRequires(self):
        pass

    def speedSales(self):
        pass

    def resales(self):
        pass

def console():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--game', default=0)
    parser.add_argument('-c', '--cell', default=0)
    parser.add_argument('-s', '--databse', default=None)
    #parser.add_argument('-n', '--name', default='Another random map')
    #parser.add_argument('-s', '--face', default=10, type=int)
    #parser.add_argument('-t', '--top', default=2.2, type=float)
    #parser.add_argument('--sharp', choise=['sharp', 'smoot'], default='smooth')
    return parser

if __name__ == '__main__':
    parser = console()
    args = parser.parse_args()

    merchant = Merchant(cursor)
    merchant.cupireRequires()
    merchant.speedSales()
    merchant.resales()

    print(",".join([str(dealId) for dealId in merchant.deals]))
