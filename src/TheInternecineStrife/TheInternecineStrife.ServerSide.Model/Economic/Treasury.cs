using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public struct GoodItem
    {
        public Good  Type;
        public float Amount;
        public float Cost
        {
            get
            {
                return Type.Price * Amount;
            }
        }
    }

    public class Treasury
    {
    	public float Gold;
    	public float Supplies;
    	public float Raw;
    	public int Weapons;
    	
    	public int Slaves;
        /// <summary>
        /// Наёмники
        /// </summary>
        public List<GoodItem> Mercenaries = new List<GoodItem>(10);

        public const double BUY_KOEFFICIENT = 1;
        public const double MERCENARY_COEFFICIENT = 3.5;
        
        public static Treasury operator +(Treasury accumulator, Treasury goods)
        {
        	var sum = new Treasury() {
        		Gold = accumulator.Gold + goods.Gold,
        		Supplies = accumulator.Supplies + goods.Supplies,
        		Raw = accumulator.Raw + goods.Raw,
        		Weapons = accumulator.Weapons + goods.Weapons,
        	};
        	sum.Slaves = accumulator.Slaves + goods.Slaves;
        	sum.Mercenaries.AddRange(accumulator.Mercenaries);
        	sum.Mercenaries.AddRange(goods.Mercenaries);
        	
            return sum;
        }

        public static Treasury operator *(Treasury source, float koefficient)
        {
            return new Treasury {
                Gold = koefficient * source.Gold,
                Supplies = koefficient * source.Supplies,
                Raw = koefficient * source.Raw,
                Weapons = (int) koefficient * source.Weapons,
                Slaves = (int) koefficient * source.Slaves,
                Mercenaries = source.Mercenaries
            };
        }

        public static Treasury operator -(Treasury from, Treasury to)
        {
            from.Gold -= to.Gold;
            from.Raw -= to.Raw;
            from.Slaves -= to.Slaves;
            from.Supplies -= to.Supplies;
            from.Weapons -= to.Weapons;
            return from;
        }

        internal void Flush()
        {
            Gold = 0;
            Supplies = 0;
            Raw = 0;
            Weapons = 0;
            Slaves = 0;
            Mercenaries.Clear();
        }

        public override string ToString()
        {
            return Gold.ToString("0.00");
        }
    }
}
