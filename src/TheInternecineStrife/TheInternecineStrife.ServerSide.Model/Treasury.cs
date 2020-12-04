using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;

namespace TheInternecineStrife.ServerSide.Model
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
        public GoodItem Gold = new GoodItem
        {
        	Type = Good.Resources[1-1],
            Amount = 0
        };
        public GoodItem Supplies = new GoodItem()
        {
            Type = Good.Resources[2-1],
            Amount = 0
        };
        public GoodItem Slaves = new GoodItem
        {
        	Type = Good.Resources[3-1],
            Amount = 0
        };
        public GoodItem Raw = new GoodItem
        {
            Type = Good.Resources[4-1],
            Amount = 0
        };
        public GoodItem Weapons = new GoodItem
        {
            Type = Good.Resources[7-1],
            Amount = 0
        };
        
        /// <summary>
        /// Наёмники
        /// </summary>
        public List<GoodItem> Mercenaries = new List<GoodItem>();

        public const double BUY_KOEFFICIENT = 1;
        public const double MERCENARY_COEFFICIENT = 3.5;
        public double Cost {
            get
            {
                return BUY_KOEFFICIENT * (
                    Gold.Cost + Supplies.Cost + Raw.Cost + Weapons.Cost + Slaves.Cost 
                    + Mercenaries.Sum((GoodItem squid) => { return squid.Cost; })
                );
            }
        }

        public Treasury(Age era = Age.StoneAge)
        {
            
        }

        public static Treasury operator +(Treasury accumulator, Treasury source)
        {
            return new Treasury {
        		Gold = new Good{Type=accumulator.Gold.Type, accumulator.Gold + source.Gold},
                Raw = accumulator.Raw + source.Raw,
                Supplies = accumulator.Supplies + source.Supplies,
                Slaves = accumulator.Slaves + source.Slaves,
                Weapons = accumulator.Weapons + source.Weapons,
                Mercenaries = new ObservableCollection<GoodItem>(accumulator.Mercenaries.AddRange(source.Mercenaries))
            };
        }

        public static Treasury operator *(Treasury source, double koefficient)
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
            Gold.Amount = 0;
            Supplies.Amount = 0;
            Raw.Amount = 0;
            Weapons.Amount = 0;
            Slaves.Amount = 0;
            Mercenaries.Clear();
        }

        public override string ToString()
        {
            return Gold.ToString("0.00");
        }

        #region INotifyPropertyChanged implementation

        public event PropertyChangedEventHandler PropertyChanged;
        protected void NotifyPropertyChanged(String propertyName = "")
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        #endregion

    }
}
