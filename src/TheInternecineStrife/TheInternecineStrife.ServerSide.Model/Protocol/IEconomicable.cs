using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Economic;

namespace TheInternecineStrife.ServerSide.Model.Protocol
{
    interface IEconomicable
    {
        Treasury Economic { get; set; }
        float Product(int day, float instrument);
        Social.CraftOrder Order { get; set; }
        List<Social.CraftOrder> Tenders { get; }
    }
}
