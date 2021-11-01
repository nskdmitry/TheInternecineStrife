using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.Online.Models;

namespace TheInternecineStrife.Online.Interfaces
{
    public interface IWeapon
    {
        IEnumerable<Weapon> Weapons { get; }
        Weapon Get(int id);
        Weapon Search(string name);
    }
}
