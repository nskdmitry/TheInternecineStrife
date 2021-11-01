using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.ServerSide.Model;

namespace TheInternecineStrife.Online.Interfaces
{
    public interface IEpidemy
    {
        IList<Epidemy> Epidemies { get; }
        Epidemy Get(int id);
    }
}
