using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class TrainingCamp : Institution
    {
        public override float Product(float instruments)
        {
            if (Clients == null || Workers == null || (Clients.Strength > 0) || (Workers.Man > 0))
            {
                return 0;
            }
            var dayPrice = CalcCosts(Workers.Man);
            if (FeasableIncome(dayPrice))
            {
                return 0;
            }

            Withdraw(dayPrice);
            Clients.Experience += instruments;

            return 0;
        }

        public override bool WorkOn(StratumClass @class)
        {
            return @class.Id == StratumClass.Classes[0].Id;
        }

        private static readonly PriceOf Cost = new PriceOf(0.001f, 0.025f, 0.005f, 1, 0.25f, 0);

        protected override bool FeasableIncome(Treasury income)
        {
            return Gold < income.Gold ||
                Food < income.Food ||
                Fuel < income.Fuel ||
                WeaponArmor < income.WeaponArmor ||
                Catridges < income.Catridges;
        }

        public override Treasury CalcCosts(int workers)
        {
            return new Wagoon
            {
                Gold = workers * Cost.Gold,
                Food = Clients.Strength * Cost.Food,
                Fuel = Cost.Fuel,
                WeaponArmor = Clients.Strength * (Cost.WeaponArmor),
                Catridges = Clients.Profile.Range != null ? Clients.Strength * Cost.Catridges : 0
            };
        }
    }
}
