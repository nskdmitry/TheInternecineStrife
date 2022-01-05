using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.Economic;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.ServerSide.Model.War
{
    public class Fortress : Protocol.Controllable, Protocol.IEconomicable
    {
        // Стены
        public WallOptions Walls { get; protected set; }
        // 
        public Division Garrison { get; protected set; }
        public Division Artillery { get; protected set; }

        public Treasury Economic { get; set; }
        public CraftOrder Order { get; set; }
        public List<CraftOrder> Tenders => new List<CraftOrder>((int)AllProduction.SeigeTechnic+1);

        public float Product(int day, float instrument)
        {
            if ((Order is null || !Order.Actual) && !(Economic is Brothel))
            {
                return 0;
            }
            var masters = (Economic as Shop);
            if (masters.Need)
            {
                DefineTender(masters.Food, AllProduction.Food);
                DefineTender(masters.Fuel, AllProduction.Fuel);
                DefineTender(masters.Catridges, AllProduction.Catridges);
                DefineTender(masters.SourceMaterials, AllProduction.Source);
                DefineTender(masters.WeaponArmor, AllProduction.Weapon);
            }
            float producted = Economic.Product(instrument);
            if (Artillery is null)
            {
                Artillery = new Division(
                    String.Format("Fortress {0} Artillery", Name),
                    day,
                    Owner,
                    (Economic as SeigeWorkshop).MachineClass,
                    ContractClass.Regulary,
                    StrongNominal.Hundred
                )
                { Strength = 0 };
            }
            if (Economic is SeigeWorkshop)
            {
                Artillery.Strength += (int)producted;
                (Economic as SeigeWorkshop).Completed -= (int)producted;
                Order.Left -= producted;
            } else if (Economic is Workshop)
            {
                Economic.WeaponArmor += producted;
            }
            return producted;
        }

        protected bool CheckTenderExists(float requirement, AllProduction need)
        {
            if (requirement > 0)
            {
                return Tenders.Find(order => order.Actual && order.Left >= requirement && order.Ware == need) != null;
            }
            return false;
        }

        protected void DefineTender(float volume, AllProduction requirement)
        {
            CraftOrder tender;
            if (!CheckTenderExists(volume, requirement))
            {
                // Item2 - цена продажи на глобальный рынок, она всегда ниже. 
                // Разумеется, потребитель хочет получить товар по этой цене или даже ниже.
                tender = new CraftOrder(Economic.Id, requirement, volume, GlobalPriceTable.PriceOf[requirement].Item2*volume);
            }
        }
    }

}
