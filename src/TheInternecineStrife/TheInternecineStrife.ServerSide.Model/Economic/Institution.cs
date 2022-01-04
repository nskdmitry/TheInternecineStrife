using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public abstract class Institution : Treasury
    {
        public Social.Stratum Workers {
            get => workers;
            set
            {
                if (value == null || !WorkOn(value.Class))
                {
                    throw new InvalidCastException("Это сословие не может работать на подобных работах");
                }
                workers = value;
            }
        }
        public War.Division Clients { get; set; }

        private new float Cattle { get; } = 0;
        private new float SourceMaterials { get; } = 0;

        public abstract override float Product(float instruments);
        public abstract bool WorkOn(Social.StratumClass @class);
        public abstract Treasury CalcCosts(int workers);
        private Social.Stratum workers;
    }
}
