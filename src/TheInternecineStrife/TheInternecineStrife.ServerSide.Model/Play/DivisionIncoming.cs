using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.ServerSide.Model.Play
{
    public enum ComingTo { Camp, MercenaryPost, TownGarrison, Castle };

    public class DivisionIncoming
    {
        public Division Division { get; set; }
        public Cell From { get; set; }
        public Cell To { get; set; }
        public int LeftTime { get; set; }
        public int PathLength { get; set; }
        public ComingTo Target { get; set; }
        public bool Invited { get; set; }
    }
}
