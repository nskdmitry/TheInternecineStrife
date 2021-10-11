using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.ServerSide.Model;

namespace TheInternecineStrife.Online.Models
{
    public class Landscape : LandType
    {
        public int TextureId { get; set; }
        
        public Landscape(int id, string name, int populationLimit, float taxLimit, float cross, bool civil = false, PlaceType place = PlaceType.Earth, CellProfile profile = CellProfile.WarOnly, Age level = Age.StoneAge) : 
            base(id, name, populationLimit, taxLimit, cross, civil, place, profile, level)
        {
        }

        public Landscape(int id, LandType land) : base(id, land.Name, land.Hobbitable, land.YieldLimit, land.Cross, land.Civilization, land.Envirounment, land.Orient, land.Level)
        {
            Capacity = land.Capacity;
            this.Comfort = land.Comfort;
            this.High = land.High;
            this.Low = land.Low;
            this.YieldStart = land.YieldStart;
        }
    }
}
