using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public sealed class PriceOf : Treasury
    {
        private float _gold;

        public new float Gold { get => _gold; private set => _gold = value >= 0 ? value : 0; }
        public new float Food { get => _food; private set => _food = value >= 0 ? value : 0; }
        public new float Fuel { get => _oil; private set => _oil = value >= 0 ? value : 0; }
        public new float Cattle { get => 0; }
        public new float Catridges { get => _arrows; private set => _arrows = value >= 0 ? value : 0; }
        public new float WeaponArmor { get => _equip; private set => _equip = value >= 0 ? value : 0; }
        public new float SourceMaterials { get => _sources; private set => _sources = value >= 0 ? value : 0; }

        public PriceOf(
            float inGold,
            float inFood,
            float inFuel,
            float inCattriges,
            float inArmory,
            float inSource
            ) : base()
        {
            Gold = inGold;
            Food = inFood;
            Fuel = inFuel;
            Catridges = inCattriges;
            WeaponArmor = inArmory;
            SourceMaterials = inSource;
        }
    }
}
