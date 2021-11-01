using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TheInternecineStrife.Online.Interfaces
{
    public interface IRegiment
    {
        List<Models.Regiment> GetMyRegiments(int idFeodal);
        List<Models.Regiment> GetArmyForces(int idArmy);
        //Models.Regiment DeclareNewRegiment(string name, Cell cell, Models.SoldierClass warclass, bool regular);
    }
}
