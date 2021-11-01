using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TheInternecineStrife.Online.Interfaces
{
    public interface IArmies
    {
        List<Models.Army> WholeArmies { get; }
        List<Models.Army> MyArmies(int idFeodal);
        Models.Army GetById(int id);
        //Models.Army HarrisonOf(Cell int);
    }
}
