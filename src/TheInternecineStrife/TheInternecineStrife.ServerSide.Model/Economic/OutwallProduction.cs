using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class OutwallProduction : Treasury
    {
        public Cell Place { get; protected set; }

        public OutwallProduction(Cell placement)
        {
            var media = placement.Background.Envirounment;
            if (media == PlaceType.Air || media == PlaceType.Bridge || media == PlaceType.Water)
            {
                throw new InvalidCastException("Подобного рода предприятия создаются на земле.");
            }
            Place = placement;
        }
    }
}
