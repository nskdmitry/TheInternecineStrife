using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Social
{
    public struct ThewLordInform
    {
        public int LordId;
        public string NameOfLord;
        public bool Active;
        public Tuple<int, int> Capital;
        public int DomainsCells;
        public int DomainsCount;
        public int Knights;
        public int Merchantes;
        public int Peasants;
        public int Womans;
        public int Childs;
        public List<Dwelling> Dwellings;

    }

    /// <summary>
    /// Собиратели информации.
    /// </summary>
    public static class ThewGuild
    {
        public static object GameState;
        public static ThewLordInform CollectInfoAbout(Lord lord)
        {
            return new ThewLordInform {
                LordId = lord.Id,
                NameOfLord = lord.Name,
                Active = lord.Active,
            };
        }
    }
}
