using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.Online.Models;
using TheInternecineStrife.ServerSide.Model;

namespace TheInternecineStrife.Online.Mocks
{
    public class MockLandscapeSet : Interfaces.ILandscapes
    {
        private readonly List<Landscape> _set = new List<Landscape>(100);

        public MockLandscapeSet()
        {
            _set.Add(new Landscape(0, "Air", 0, 0, 0, false, PlaceType.Air, CellProfile.Agrary, Age.StoneAge) { TextureId = 2 });
            foreach (var item in LandType.Set)
            {
                var terra = item.Value;
                _set.Add(new Landscape(terra.Id + 1, terra) { TextureId = terra.Id + 3 });
            }
        }

        public Landscape GetLandscape(int id)
        {
            return _set.ElementAt(id);
        }

        public IEnumerable<Landscape> Landscapes
        {
            get { return _set; }
        }
    }
}
