using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.ServerSide;

namespace TheInternecineStrife.Online.Models
{
    public class Dwelling : ServerSide.Model.Dwelling
    {
        public int ClassID { get; set; }
        public int GuardID { get; set; }
    }
}
