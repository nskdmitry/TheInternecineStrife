using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.ServerSide.Model;

namespace TheInternecineStrife.Online.Models
{
    public class Epoch
    {
        public Age Id { get; set; }
        public string Name { get; set; }
        public int DefaultWarMode { get; }
        public float[] MiningVolues { get; }
    }
}
