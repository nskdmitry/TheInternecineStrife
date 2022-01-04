using System;
using TheInternecineStrife.ServerSide.Model.Social;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public sealed class SeigeWorkshop : Shop
    {
        public SoldierProfile MachineClass { get; private set; }
        public int Completed {
            get => (int)Math.Floor(stored);
            set {
                if (value > stored)
                {
                    return;
                }
                stored = value > 0? value : 0;
            }
        }

        public SeigeWorkshop(Stratum masters, SoldierProfile of) : base(masters)
        {
            if (!of.Machined)
            {
                throw new InvalidCastException("Это не бараки, это осадная мастерская!");
            }
            MachineClass = of;
            Cost = MachineClass.Price;
            ManDailyProgress = 0.25f;
        }

        public override float Product(float instruments)
        {
            var product = base.Product(instruments);
            stored += product;
            return (float)Math.Floor(product);
        }

        private float stored = 0;
    }
}
