using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.Online.Models;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.Online.Mocks
{
    public class MockSoldierProfiles : Interfaces.ISoldierProfile
    {
        public MockSoldierProfiles()
        {
            List.Add(new SoldierClass(false) {
                Id = 1,
                Name = "Безоружный",
                Malee = new Models.Weapon(new ServerSide.Model.War.Weapon() { Id = 0}, 22),
                Speed = SoldierProfile.LIGHT_RUN_SPEED,
                TextureId = 22,
                From = ServerSide.Model.Age.StoneAge
            });
            List.Add(new SoldierClass(false) {
                Id = 2,
                Name = "Пращник",
                Range = new Models.Weapon(new ServerSide.Model.War.Weapon() { Id = 1 }, 23),
                Speed = SoldierProfile.LIGHT_RUN_SPEED,
                TextureId = 23,
                From = ServerSide.Model.Age.StoneAge
            });
            List.Add(new SoldierClass(false) {
                Id = 3,
                Name = "Ополченец",
                Malee = new Models.Weapon(new ServerSide.Model.War.Weapon() { Id = 2 }, 24),
                Speed = SoldierProfile.LIGHT_RUN_SPEED,
                TextureId = 24,
                From = ServerSide.Model.Age.StoneAge
            });
            List.Add(new SoldierClass(false) {
                Id = 4,
                Name = "Лучник",
                Range = new Models.Weapon(new ServerSide.Model.War.Weapon() { Id = 4}, 25),
                Speed = SoldierProfile.LIGHT_RUN_SPEED,
                From = ServerSide.Model.Age.StoneAge
            });
            List.Add(new SoldierClass(false)
            {
                Id = 5,
                Name = ""
            });
        }

        public List<SoldierProfile> List { get; } = new List<SoldierProfile>(25);

        public SoldierProfile Get(uint id)
        {
            return List[(int)id - 1];
        }
    }
}
