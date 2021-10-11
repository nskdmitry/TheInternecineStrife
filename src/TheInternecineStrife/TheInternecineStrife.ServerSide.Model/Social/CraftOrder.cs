using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Social
{
    /// <summary>
    /// Заказ для сословия на выполнение работ. Как правило: создать или приобрести оружие, купить/добыть ресурсы, построить осадные машины.
    /// </summary>
    public class CraftOrder
    {
        public readonly float Volume;
        public float Left;


        public CraftOrder(int volume)
        {
            Volume = volume;
            Left = volume;
        }
    }
}
