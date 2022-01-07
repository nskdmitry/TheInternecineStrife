using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public enum AllProduction { None, Food, Cattle, Fuel, Gold, Source, Catridges, Weapon, SeigeTechnic };

    public class Treasury
    {
        public int Id { get; set; }
        /// <summary>
        /// Поддерживается механизм долга:)
        /// </summary>
        public float Gold { get; set; } = 0;
        public float Food { get => _food; set => _food = value >= 0 ? value : 0; }
        public float Fuel { get => _oil; set => _oil = value >= 0 ? value : 0; }
        public float Cattle { get => (float)_rams; set => _rams = value >= 0 ? (int)value : 0; }
        public float Catridges { get => _arrows; set => _arrows = value >= 0 ? value : 0; }
        public float WeaponArmor { get => _equip; set => _equip = value >= 0 ? value : 0; }
        public float SourceMaterials { get => _sources; set => _sources = value >= 0 ? value : 0; }
        
        public static Treasury operator +(Treasury stock, Treasury source)
        {
            stock.Gold += source.Gold;
            stock.Food += source.Food;
            stock.Fuel += source.Fuel;
            stock.Cattle += source.Cattle;
            stock.Catridges += source.Catridges;
            stock.WeaponArmor += source.WeaponArmor;
            stock.SourceMaterials += stock.SourceMaterials;
            return stock;
        }

        public static Treasury operator-(Treasury price)
        {
            return new Treasury
            {
                Catridges = -price.Catridges,
                Cattle = -price.Cattle,
                Gold = -price.Gold,
                Food = -price.Food,
                Fuel = -price.Fuel,
                SourceMaterials = -price.SourceMaterials,
                WeaponArmor = -price.WeaponArmor,
            };
        }

        public Treasury Withdraw(Treasury resources)
        {
            resources.Catridges = Math.Min(resources.Catridges, Catridges);
            resources.Cattle = Math.Min(resources.Cattle, Cattle);
            resources.Gold = Math.Min(resources.Gold, Gold);
            resources.Food = Math.Min(resources.Food, Food);
            resources.Fuel = Math.Min(resources.Fuel, Fuel);
            resources.SourceMaterials = Math.Min(resources.SourceMaterials, SourceMaterials);
            resources.WeaponArmor = Math.Min(resources.WeaponArmor, WeaponArmor);

            Catridges -= resources.Catridges;
            Cattle -= resources.Cattle;
            Gold -= resources.Gold;
            Food -= resources.Food;
            Fuel -= resources.Fuel;
            SourceMaterials -= resources.SourceMaterials;
            WeaponArmor -= resources.WeaponArmor;

            return resources;
        }

        public virtual float Product(float instruments)
        {
            return 0;
        }

        protected virtual bool FeasableOutcome(Treasury outcome)
        {
            return Gold < outcome.Gold;
        }

        protected float _food = 0;
        protected float _arrows = 0;
        protected float _equip = 0;
        protected float _sources = 0;
        protected float _oil = 0;
        protected int _rams = 0;
    }
}
