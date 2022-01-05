using System;
using TheInternecineStrife.ServerSide.Model.Economic;

namespace TheInternecineStrife.ServerSide.Model.Social
{
    /// <summary>
    /// Заказ для сословия на выполнение работ. Как правило: создать или приобрести оружие, купить/добыть ресурсы, построить осадные машины.
    /// </summary>
    public class CraftOrder
    {
        public readonly float Volume;
        public float Left { get; set; }
        public AllProduction Ware { protected set; get; }
        public bool Actual { get => Left > 0; }
        public int IdAssumer { get; }
        public float Payment { get; set; }

        public CraftOrder(int needer, AllProduction ware, float volume, float price)
        {
            IdAssumer = needer;
            Volume = volume;
            Left = volume;
            Payment = price;
            Ware = ware;
            carrier = MiddlemanFabric.AssignMiddlemanForTook(Ware);
        }

        public float TakeFrom(Treasury provider)
        {
            var amount = Math.Min(carrier(provider), Left);
            Left -= amount;
            return amount;
        }

        private readonly Middleman carrier;
    }
}