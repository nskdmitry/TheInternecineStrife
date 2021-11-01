using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TheInternecineStrife.Online.Interfaces
{
    public interface IPopulations
    {
        Models.Population Get(int id);
        Models.Population Of(uint idPlace);
        Models.Population Put(Models.Population population);
        Models.Population Update(int id, Models.Population population);
    }
}
