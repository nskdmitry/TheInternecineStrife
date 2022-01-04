using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class Brothel : Institution
    {
        private new float Catridges { get; } = 0;
        private new float WeaponArmor { get; } = 0;

        public override float Product(float instruments)
        {
            var clientGirlPairsCount = GetRealClientsAmount();
            var circleCost = CalcCosts(clientGirlPairsCount);
            Withdraw(circleCost);
            return SexServiceIncome(clientGirlPairsCount);
        }

        public override bool WorkOn(StratumClass @class)
        {
            return @class.Id != StratumClass.Classes[6].Id;
        }

        public override Treasury CalcCosts(int girls)
        {
            return new Treasury
            {
                Gold = CostPerGirl.Gold * girls,
                Food = CostPerGirl.Food * girls,
                Fuel = CostPerGirl.Fuel,
            };
        }
        public float CalcIncomesFrom(int girls)
        {
            return LOVE_PRICE * girls;
        }

        public int GetRealClientsAmount()
        {
            return Math.Min(DAILY_CLIENTS_LIMIT * Workers.Feman
                , Math.Min(Clients.Strength, (int)(Clients.Baggage.Gold / LOVE_PRICE)));
        }

        private readonly PriceOf CostPerGirl = new PriceOf(0.0002f, 1/5, 5/2, 0, 0, 0);

        private float SexServiceIncome(int clientsServised)
        {
            Consequences(clientsServised);

            Clients.Energy = Math.Min(1f, Clients.Energy +  (float)(clientsServised/(int)Clients.Contract.Nominal));
            float finalSum = CalcIncomesFrom(clientsServised);
            Clients.Baggage.Gold -= finalSum;
            Gold += finalSum;
            return finalSum;
        }

        private void Consequences(int servicedClientedCount)
        {
            var seed = servicedClientedCount + Workers.Feman + Workers.Kids + Workers.Man;
            var dice = new Random(seed);
            int usingLevel = servicedClientedCount / Workers.Feman;
            var girlsDied = Math.Max(usingLevel - dice.Next(Workers.Feman), Workers.AdultedWomen);
            int offspring = dice.Next(Math.Min(usingLevel, Workers.Feman));

            Workers.Feman -= girlsDied;
            Workers.Kids += offspring;
        }
        
        protected const float LOVE_PRICE = 0.1f;
        protected const int DAILY_CLIENTS_LIMIT = 12;
    }
}
