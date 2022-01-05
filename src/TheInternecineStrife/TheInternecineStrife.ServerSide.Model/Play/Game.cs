using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Play
{
    public class Game
    {
        public uint Id { get; set; }
        public string Name { get; set; }
        public GameFrame Status { get; set; }
        //public War.Army LastActive { get; set; }

        public DateTime CreatedAt { get; set; }
    }
}
