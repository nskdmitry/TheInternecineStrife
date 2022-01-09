using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Protocol;
using TheInternecineStrife.ServerSide.Model.Social;
using TheInternecineStrife.ServerSide.Model.World;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class Exchequer : FinanceCenter
    {
        public float Tax { get; set; }

        public Exchequer(Map world, IEconomicable of, Stratum workers) : base(world, of, workers)
        {
        }

        public override float Product(float instruments)
        {
            var selectDomainCells = World.Ground.Where(cell => cell.Settling?.Region.Capital.Id == ServicesInstance.Id);
            var collectSum = selectDomainCells.Sum(cell => CollectAndCountTaxes(cell.Population));
            return base.Product(instruments);
        }

        private float CollectAndCountTaxes(Population civils)
        {
            var collectedFromMerchanters = CollectTaxesFrom(civils.Merchantes);
            var collectedFromCrafters = CollectTaxesFrom(civils.ArtistCraft);
            var collectedFromFreeman = CollectTaxesFrom(civils.Freeman);
            var collectedFromSerfs = CollectTaxesFrom(civils.Serfs);
            return collectedFromMerchanters + collectedFromCrafters + collectedFromFreeman + collectedFromSerfs;
        }

        private float CollectTaxesFrom(Stratum layer)
        {
            var collectedCoins = Math.Min(layer.Man * Tax, layer.Founds);
            layer.Founds -= collectedCoins;
            return collectedCoins;
        }
    }
}
