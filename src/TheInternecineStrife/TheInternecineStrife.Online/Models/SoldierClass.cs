using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.Online.Models
{
    public class SoldierClass : SoldierProfile
    {
        public int TextureId { get; set; }

        public SoldierClass(bool machined) : base()
        {
            Machined = machined;
        }

        public SoldierClass(SoldierProfile basic)
        {
            Id = basic.Id;
            Name = basic.Name;
            From = basic.From;
            Health = basic.Health;
            Speed = basic.Speed;
            Range = basic.Range;
            Malee = basic.Malee;
            Machined = basic.Machined;
        }
    }
}
