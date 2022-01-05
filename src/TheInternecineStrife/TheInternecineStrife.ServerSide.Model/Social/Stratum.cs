using System;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.ServerSide.Model.Social
{
    public delegate void StratumProduction(Stratum group, Cell place);
    public delegate void RecruitToMilitary(Stratum group, Army military);

    /// <summary>
    /// Сословная группа - конкретная часть населения, относящаяся к сословию.
    /// Помимо мужчин, содержит также и женщин с детьми.
    /// </summary>
    public class Stratum
    {
        private static Random r = new Random();

        public readonly StratumClass Class;
        public int Man { get; set; }
        public int Feman { get; set; }
        public int Kids { get; set; }
        public int Called {
            get { return _calls; }
            protected set
            {
                if (_calls == value)
                {
                    return;
                }
                _satisfaction -= (float)((value - _calls) * 0.1);
                _calls = value;
            }
        }
        public float Satisfaction {
            get { return _satisfaction; }
            set { _satisfaction = Math.Min(1f, value); }
        }
        public CraftOrder CurrentOrder;
        public int AdultedMen { get; protected set; }
        public int AdultedWomen { get; protected set; }
        public float Founds { get; set; } = 0;

        public Army CallMilitary(Age age, Army force = null)
        {
            var strength = Called < 3 ? r.Next(Man / Called) : 0;
            if (strength == 0)
            {
                throw new Exception("Никто не откликнулся");
            }

            var military = new Division("", 0, null, Class.MilitaryClasses[age], ContractClass.Military, StrongNominal.Hundred);
            var side = (int)(Math.Floor(Math.Sqrt(strength + military.Strength)));
            // Как отряд будет сражаться:
            var formation = new War.Battle.Formation();
            military.Formation = formation;
            if (force == null)
            {
                force = new Army();
                force.Stacks[0] = military;
            }
            if (Class.MilitaryClasses.Values.Count > 0)
            {
                var militaryClass = Class.MilitaryClasses[age];

                formation.Columns = side;
                formation.Rows = (int)Math.Ceiling((double)side);
                formation.Density = 1; // плотность построения ч-к/м2
                formation.RangeAttackDistance = militaryClass.Range.Far - 1f; // с какого расстояния начать обстрел
                formation.RetreetDistance = -militaryClass.Malee.Near; // если враг ближе чем, отступать
                formation.MaleeAttackDistance = militaryClass.Malee.Far; // на каком расстоянии переходить к рукопашной
                formation.MaleeResource = 1000; // Сколько циклов может рубиться
                formation.RangeResource = 10; // Запас стрел или других снарядов
                formation.NoBlendMalee = militaryClass.Malee.Damage > militaryClass.Range.Damage;
                formation.Ranger = formation.NoBlendMalee;
                formation.FireOnMarsh = false; // это конный лучник, стреляющий на ходу?
            } else
            {
                Class.CallToMilitary(this, force);
            }
            return force;
        }

        private int _calls;
        private float _satisfaction;

        public Stratum(StratumClass socium)
        {
            Class = socium;
            Man = 0;
            Feman = 0;
            Kids = 0;
            _calls = 0;
            _satisfaction = 1;

            AdultedMen = 0;
            AdultedWomen = 0;
        }

        public void NextGeneration()
        {
            var fellows = r.Next(0, (int)(Kids * 2 / 3));
            var girls = Kids - fellows;
            Man -= AdultedMen + fellows;
            Feman -= AdultedWomen + girls;
            Kids = 0;
            AdultedMen = fellows;
            AdultedWomen = girls;
        }
    }
}
