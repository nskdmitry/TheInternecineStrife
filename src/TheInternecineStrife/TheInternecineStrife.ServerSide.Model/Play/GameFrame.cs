using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Play
{
    public class GameFrame
    {
        public uint Id { get; set; }
        public uint GameId { get; set; }
        public World.Map Playground { get; set; }
        public DateTime Updated { get; set; }
        public int PlayholderId { get; set; } // Игрок, сделавший ход
        public int CircleNo { get; set; }
        public List<DivisionIncoming> DivisionsInRun { get; } = new List<DivisionIncoming>(10);
    }
}
