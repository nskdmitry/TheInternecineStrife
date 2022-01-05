using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.World
{
    public class Map
    {
        public uint Id { get; set; }
        public string Name { get; set; }
        public uint Face { get; set; }
        public Cell[] Ground { get; set; }
        public List<Domain> Domains { get; set; }
        public List<Dwelling> Dwellings { get; set; }
        public List<War.Army> Armies { get; set; }

        /*
         * None-playable metainformation.
         */
        public string GeneratorName { get; set; }
        public DateTime Created { get; set; }
        public string Author { get; set; }

        public uint GetCellIndex(uint x, uint y) => x + y * Face;
    }
}
