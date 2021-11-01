using System.Collections.Generic;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.Online.Interfaces
{
    public interface IStratum
    {
        IEnumerable<StratumClass> GetAllStratumClasses();
        StratumClass GetClass(int id);

        IEnumerable<Models.Stratum> GetStratasOf(int idPopulation);
        Models.Stratum Get(int id);
        Models.Stratum Put(Models.Stratum stratum);
        Models.Stratum Update(Models.Stratum stratum);
    }
}
