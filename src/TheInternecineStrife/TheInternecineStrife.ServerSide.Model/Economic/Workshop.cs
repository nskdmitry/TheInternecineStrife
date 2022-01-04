using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public enum Manufacture {
        None = AllProduction.None,
        Weapon = AllProduction.Weapon,
        Catridges = AllProduction.Catridges
    };

    /// <summary>
    /// Посады, они же манифактуры и цеха.
    /// Потребляют: пищу, сырьё, топливо и золото.
    /// 
    /// </summary>
    public sealed class Workshop : Shop
    {
        public Manufacture Production { get; private set; }

        public Workshop(Manufacture wares, Stratum artisans, Treasury startup = null) : base(artisans)
        {
            Production = wares;
            if (startup is Treasury && startup != null)
            {
                Gold = startup.Gold;
                Food = startup.Food;
                Fuel = startup.Fuel;
                SourceMaterials = startup.SourceMaterials;
            }
            switch (Production)
            {
                case Manufacture.Catridges:
                    Cost = CatridgeCost;
                    ManDailyProgress = CatridgerPerManDay;
                    break;
                case Manufacture.Weapon:
                    Cost = EquipmentCost;
                    ManDailyProgress = EquipPerManDay;
                    break;
                case Manufacture.None:
                default:
                    throw new InvalidCastException("Что производит эта мастерская?");
            }
        }

        public override float Product(float instruments)
        {
            float producted = 0;
            var capability = new float[5];
            producted = base.Product(instruments);

            switch (Production)
            {
                case Manufacture.Weapon:
                    if (producted > 0) WeaponArmor += producted;
                    break;
                case Manufacture.Catridges:
                    if (producted > 0) Catridges += producted;
                    break;
                default:
                    break;
            }
            
            return producted;
        }

        // Стоимость производства
        public const float CatridgerPerManDay = 6;
        public const float EquipPerManDay = 0.2f;
        private readonly Treasury CatridgeCost = new Treasury
        {
            Gold = 0.01f,
            Food = 0,
            Fuel = 0.01f,
            SourceMaterials = 0.3f,
            WeaponArmor = 0,
            Cattle = 0,
            Catridges = 0,
        };
        private readonly Treasury EquipmentCost = new Treasury
        {
            Gold = 1.2f,
            Food = 0.01f,
            Fuel = 2.9f,
            SourceMaterials = 3.2f,
            WeaponArmor = 0,
            Cattle = 0,
            Catridges = 0
        };
    }
}
