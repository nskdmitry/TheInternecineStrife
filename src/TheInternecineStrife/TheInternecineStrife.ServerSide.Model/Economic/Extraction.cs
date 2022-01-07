using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public enum Resource { Gold, Fuel, Source, None };

    /// <summary>
    /// Место добычи ресурсов
    /// </summary>
    public sealed class Extraction : OutwallProduction
    {
        public Resource Material { get => _excavate; set {
                _excavate = value != Resource.None ? value : _excavate;
                switch (Material)
                {
                    case Resource.Gold:
                        Amount = GoldOnStart;
                        Available = Gold;
                        break;
                    case Resource.Source:
                        Amount = SourceOnStart;
                        Available = SourceMaterials;
                        break;
                    case Resource.Fuel:
                        Amount = FuelOnStart;
                        Available = Fuel;
                        break;
                }
            }
        }
        public readonly float Profit;
        public readonly int Wide;
        public bool Opened { get => _excavate != Resource.None; }

        public Stratum Workers { get; private set; }
        // Доступно и сколько было. Зависят от типа ресурсов, добываемых в этом месте.
        public float Available { get; private set; }
        public float Amount { get; private set; }

        public new float Gold { private set; get; }
        public new float Fuel { private set { _oil = value >= 0 ? value : 0; } get => _oil; }
        public new float SourceMaterials { private set => _sources = value >= 0 ? value : 0; get => _sources; }

        private readonly float GoldOnStart;
        private readonly float FuelOnStart;
        private readonly float SourceOnStart;

        public Extraction(Treasury rich, float profit, int size, Cell cell) : base(cell)
        {
            GoldOnStart = rich.Gold;
            FuelOnStart = rich.Fuel;
            SourceOnStart = rich.SourceMaterials;

            Gold = GoldOnStart;
            Fuel = FuelOnStart;
            SourceMaterials = SourceOnStart;
        }

        public float CurrentProfit(float instrument)
        {
            return Math.Min(Profit, instrument) * Available / Amount;
        }

        /// <summary>
        /// Добыча ресурсов
        /// </summary>
        /// <param name="workers">Число рабочих</param>
        /// <param name="instrument">Эффективность рабты инструментом: объ./чел*ход</param>
        /// <returns>Сколько добыто в ход</returns>
        public override float Product(float instrument)
        {
            var sum = Math.Min(Available, CurrentProfit(instrument) * Math.Min((Workers.AdultedMen + Workers.Man), Wide));
            Available -= sum;
            switch (Material)
            {
                case Resource.Gold: Gold = Available; break;
                case Resource.Source: SourceMaterials = Available; break;
                case Resource.Fuel: Fuel = Available; break;
            }
            Workers.Man = Math.Max(Workers.Man - 2, 0);
            if (Material == Resource.Gold)
            {
                Workers.Man = Math.Max(Workers.Man - 5, 0);
            }
            return sum;
        }

        // No product, no manifacture, extraction only
        private Resource _excavate = Resource.None;
        private new float Food { set; get; }
        private new float Cattle { get; set; }
        private new float Catridges { set; get; }
        private new float WeaponArmor { get; set; }
    }
}
