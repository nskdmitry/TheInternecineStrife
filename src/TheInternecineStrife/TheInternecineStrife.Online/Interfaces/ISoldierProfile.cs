using System.Collections.Generic;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.Online.Interfaces
{
    public interface ISoldierProfile
    {
        SoldierProfile Get(uint id);
        List<SoldierProfile> List { get; }
    }
}
