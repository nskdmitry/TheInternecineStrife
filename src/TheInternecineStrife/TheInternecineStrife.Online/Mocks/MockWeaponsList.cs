using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.Online.Interfaces;
using TheInternecineStrife.Online.Models;

namespace TheInternecineStrife.Online.Mocks
{
    public class MockWeaponsList : IWeapon
    {
        private readonly List<Weapon> _all = new List<Weapon>(21);

        public MockWeaponsList()
        {
            foreach (var weapon in ServerSide.Model.War.Weapon.Variants)
            {
                _all.Add(new Weapon(weapon, weapon.Id + 100));
            }
        }

        public IEnumerable<Weapon> Weapons => _all;

        public Weapon Get(int id)
        {
            return _all[id - 1];
        }

        public Weapon Search(string name)
        {
            return _all.First(weapon => weapon.Name == name);
        }
    }
}
