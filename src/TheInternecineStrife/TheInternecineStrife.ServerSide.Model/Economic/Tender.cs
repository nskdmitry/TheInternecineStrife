using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class Tender
    {
        public readonly Good Type;
        public readonly float Volume;
        public float Progress { get; private set; }
        public float Left { get { return Volume - Progress; } }
        public bool IsOpen { get { return Left > 0.00 && _open; } }

        public GoodItem Close()
        {
            _open = false;
            return new GoodItem()
            {
                Type = Type,
                Amount = Progress
            };
        }

        private bool _open;
    }
}
