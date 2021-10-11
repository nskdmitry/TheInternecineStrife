using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TheInternecineStrife.Online.Interfaces
{
    public interface ILandscapes
    {
        IEnumerable<Models.Landscape> Landscapes { get; }
        Models.Landscape GetLandscape(int id);
    }
}
