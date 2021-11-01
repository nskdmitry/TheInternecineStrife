using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.War
{
    public class Armor
    {
        public uint Id { get; set; }
        public string Name { get; set; }
        public float DefenceLevel {
            get { return _surface_closed; }
            set { _surface_closed = Math.Max(0.00f, Math.Min(value, 1.00f)); }
        }
        public int Resource { get; protected set; }

        private float _surface_closed = 0;
    }
}
