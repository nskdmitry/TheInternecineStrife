using System.Collections.Generic;
using System.Linq;
using TheInternecineStrife.Online.Models;

namespace TheInternecineStrife.Online.Mocks
{
    public class MockArmies : Interfaces.IRegiment, Interfaces.IArmies
    {
        public List<Army> WholeArmies => Armies;

        public List<Army> Armies { get; set; } = new List<Army>(100);

        public List<Regiment> GetArmyForces(int idArmy)
        {
            return Armies[idArmy - 1].Stacks.Select(div => new Regiment(div)).ToList();
        }

        public Army GetById(int id)
        {
            return Armies[id - 1];
        }

        public List<Regiment> GetMyRegiments(int idFeodal)
        {
            return Armies
                .Select(army => army.Stacks)
                .Aggregate((list, append) => list.Union(append).ToArray())
                .Where(squid => squid.Owner.Id == idFeodal)
                .Select(division => new Regiment(division))
                .ToList();
        }

        public List<Army> MyArmies(int idFeodal)
        {
            return Armies.Where(army => army.Owner.Id == idFeodal).ToList();
        }
    }
}
