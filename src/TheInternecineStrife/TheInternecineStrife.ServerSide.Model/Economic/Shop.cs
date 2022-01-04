using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class Shop : Treasury
    {
        public Stratum Crafters { get; private set; }
        public Treasury Requirement { get; set; } = new Treasury();
        public bool Need { get; protected set; }
        protected Treasury Cost;
        protected float ManDailyProgress = 1;

        public Shop(Stratum masters)
        {
            if (masters.Class.Name != "ремесленники")
            {
                throw new InvalidCastException("В мастерских могут работать только ремесленники");
            }
            Crafters = masters;
        }

        public override float Product(float instruments)
        {
            // Допустим, что ресурсов хватает
            Need = false;
            // Расчёт посильных возможностей
            var byMan = Crafters.Man * instruments * ManDailyProgress;
            var capabilites = new float[]
            {
                Cost.Gold == 0 ? byMan : Gold / Cost.Gold,
                Cost.SourceMaterials == 0? byMan : SourceMaterials / Cost.SourceMaterials,
                Cost.Catridges == 0 ? byMan : Catridges / Cost.Catridges,
                Cost.WeaponArmor == 0? byMan : WeaponArmor / Cost.WeaponArmor,
                Cost.Food == 0? byMan : Food / (Crafters.Man * Cost.Food / instruments),
                Cost.Fuel == 0? byMan : Fuel / Cost.Fuel,
                byMan,
            };
            float producted = capabilites.Min();
            if (producted < 1)
            {
                // Заявить о нехватке средств.
                Need = true;
                Requirement.Catridges = Cost.Catridges * Crafters.Man - Catridges;
                Requirement.Food = Cost.Food * Crafters.Man / instruments - Food;
                Requirement.Fuel = Cost.Fuel * Crafters.Man - Fuel;
                Requirement.Gold = Cost.Gold * Crafters.Man - Gold;
                Requirement.SourceMaterials = Cost.SourceMaterials * Crafters.Man - SourceMaterials;
                Requirement.WeaponArmor = Cost.WeaponArmor * Crafters.Man - WeaponArmor;
                return 0;
            }
            float dailyPrice = Cost.Gold * producted;
            Food -= Crafters.Man / instruments;
            Gold -= dailyPrice;
            SourceMaterials -= Cost.SourceMaterials * producted;
            Fuel -= Cost.Fuel * producted;
            Catridges -= Cost.Catridges * producted;
            WeaponArmor -= Cost.WeaponArmor * producted;
            // Плата мастерам.
            Crafters.Founds += dailyPrice;
            return producted;
        }

        // Не держат скота
        private new float Cattle { get; set; }
    }
}
