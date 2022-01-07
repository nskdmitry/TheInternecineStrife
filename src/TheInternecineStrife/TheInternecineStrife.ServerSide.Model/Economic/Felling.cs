using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class Felling : OutwallProduction
    {
        public Felling(Cell cell) : base(cell)
        {
            if (cell.Background.Orient != CellProfile.Agrary)
            {
                throw new InvalidCastException("Только для аграрной местности, лучше - лесов");
            }
        }
    }
}
