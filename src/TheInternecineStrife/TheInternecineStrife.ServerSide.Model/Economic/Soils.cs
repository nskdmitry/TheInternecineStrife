using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public sealed class Soils : Treasury
    {
        public float FullSquer { get; private set; }
        public float WeedSquer { get => weeds; private set => weeds = Math.Min(FullSquer, value); }
        public float FieldSquer {
            get => FullSquer - weeds;
            set
            {
                if (value > FullSquer) return;
                if (value > FieldSquer)
                {
                    float price = (value - FieldSquer) * CostOfDeweedingM2;
                    if (price > Gold)
                    {
                        throw new ArithmeticException("Слишком много надо расчистить. Дайте денег на это!");
                    }
                    Gold -= price;
                }
                weeds = FullSquer - value;
            }
        }
        public Stratum Peasants { get; private set; }

        public Soils(float squer, LandType land, Stratum peasants = null)
        {
            FullSquer = squer;
            WeedSquer = squer;
            if (peasants != null)
            {
                if (peasants.Class.Name != "крепостные")
                {
                    throw new TypeInitializationException("На полях работают крестьяне", new InvalidCastException());
                }
                Peasants = peasants;
            }
        }

        public const float WeedNutritional = 0.2f;
        public const float WeedPerMeter = 16f;
        public const float CerealNutritional = 24f;
        public const float CerealPerMeter = 0.2f;
        public const float CostOfDeweedingM2 = 0.1f;

        // TODO Модель поедания всего скотом и выращивания пшеницы на отвоёванных у сорняков землях.
        public override float Product(float instruments)
        {
            return base.Product(instruments);
        }

        /// <summary>
        /// Почвы производят только еду. Однако золото тратится на расчистку участка и покупку зерна.
        /// </summary>
        private new float Fuel { get; set; }
        private new float Catridges { get; set; }
        private new float WeaponArmor { get; set; }
        private new float SourceMaterials { get; set; }

        private float weeds;
    }
}
