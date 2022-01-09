using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Protocol;
using TheInternecineStrife.ServerSide.Model.Social;
using TheInternecineStrife.ServerSide.Model.World;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class FinanceCenter : Treasury
    {
        public Map World { get; protected set; }
        public Stratum Workers { get; protected set; }
        public IEconomicable ServicesInstance { get; protected set; }

        public FinanceCenter(Map linkForWorld, IEconomicable of, Stratum workers)
        {
            World = linkForWorld;
            Workers = workers;
            ServicesInstance = of;
        }

        public override float Product(float instruments)
        {
            return base.Product(instruments);
        }
    }
}
