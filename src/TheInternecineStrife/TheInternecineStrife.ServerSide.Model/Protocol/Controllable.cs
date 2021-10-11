using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Protocol
{
    public abstract class Controllable
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public bool Active { get; set; }
        public Controllable Owner { get; set; }
    }
}
