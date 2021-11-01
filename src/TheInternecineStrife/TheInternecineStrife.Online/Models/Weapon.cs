using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TheInternecineStrife.Online.Models
{
    public class Weapon : ServerSide.Model.War.Weapon
    {
        public int TextureId { get; set; }

        public Weapon(ServerSide.Model.War.Weapon basic, int idTexture) : base()
        {
            Id = basic.Id;
            Name = basic.Name;
            Damage = basic.Damage;
            Far = basic.Damage;
            Near = basic.Damage;
            TextureId = idTexture;
        }
    }
}
