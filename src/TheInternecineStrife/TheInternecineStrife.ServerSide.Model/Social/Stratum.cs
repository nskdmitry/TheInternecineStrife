using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.ServerSide.Model.Social
{
    public delegate void StratumProduction(Stratum group, Cell place);
    public delegate void RecruitToMilitary(Stratum group, Army military);
    /// <summary>
    /// Сословие - группа людей по правам, доходу, возможностям и обязанностям.
    /// Сословие отвечает за функцию и то, кого можно призвать в качестве ополчения.
    /// </summary>
    public class StratumClass
    {
        public readonly int Id;
        public readonly string Name;
        public readonly bool Taxable;
        public readonly float Expenses;
        /// <summary>
        /// Как воружается сословное ополчение.
        /// </summary>
        public Dictionary<Age, SoldierProfile> MilitaryClasses;
        /// <summary>
        /// Гражданская функция сословия.
        /// </summary>
        public StratumProduction Production;
        /// <summary>
        /// Если сословие не служит, то как оно ему помогает?
        /// </summary>
        public RecruitToMilitary CallToMilitary;
        
        private StratumClass(int id, string name, bool tax, float expenseForLife = 1.0f)
        {
            Id = id;
            Name = name;
            Taxable = tax;
            Expenses = expenseForLife;
        }

        public static StratumClass[] Classes = new StratumClass[]
        {
            new StratumClass(0, "знать", false, 20) { MilitaryClasses = new Dictionary<Age, SoldierProfile> {
                {Age.StoneAge, SoldierProfile.Basic[1] },
                {Age.Neolit, SoldierProfile.Basic[8] },
                {Age.Bronze, SoldierProfile.Basic[15] },
                {Age.IronAge, SoldierProfile.Basic[22] },
                {Age.MiddleAge, SoldierProfile.Basic[29] }
            },
                // Ни хера не производят.
                Production = (Stratum group, Cell place) => { }
            },
            new StratumClass(1, "купцы", true, 10) { MilitaryClasses = new Dictionary<Age, SoldierProfile>
            {
                {Age.StoneAge, SoldierProfile.Basic[2] },
                {Age.Neolit, SoldierProfile.Basic[9] },
                {Age.Bronze, SoldierProfile.Basic[16] },
                {Age.IronAge, SoldierProfile.Basic[23] },
                {Age.MiddleAge, SoldierProfile.Basic[30] }
            },
                // Купцы приносят золото в карманы жителей поселка (свои, конечно же).
                Production = (Stratum group, Cell place) => { place.Settling.Founds = place.Settling.Founds * (1 + group.Man / 100); }
            },
            new StratumClass(2, "ремесленники", true, 8) { MilitaryClasses = new Dictionary<Age, SoldierProfile>
                {
                    {Age.StoneAge, SoldierProfile.Basic[3] },
                    {Age.Neolit, SoldierProfile.Basic[10] },
                    {Age.Bronze, SoldierProfile.Basic[17] },
                    {Age.IronAge, SoldierProfile.Basic[24] },
                    {Age.MiddleAge, SoldierProfile.Basic[31] }
                },
                // Ремесленники выполняют заказы на снаряжение войск. Нет заказа - нет работы.
                Production = (Stratum group, Cell place) => {
                    var order = group.CurrentOrder;
                    if (order == null || order.Left == 0)
                    {
                        return;
                    }
                }
            },
            new StratumClass(3, "врачи", false, 25) {
                // Врачи сокращают смертность при эпидемии.
                Production = (Stratum group, Cell place) => {
                    
                },
                // Врачи пополняют медбригады 
                CallToMilitary = (Stratum group, Army military) => { military.Formation.Medics += (new Random()).Next(group.Man); }
            },
            new StratumClass(4, "свободные", true, 0.5f) {
                // Свободные крестьяне и мещане вооружатся, чем могут
                MilitaryClasses = new Dictionary<Age, SoldierProfile> {

                },
                // Зарабатывают деньги и платят налоги
                Production = (Stratum group, Cell place) => { }
            },
            new StratumClass(5, "крепостные", true, 0.01f) {
                MilitaryClasses = new Dictionary<Age, SoldierProfile>
                {

                },
                Production = (Stratum group, Cell place) => { }
            },
            new StratumClass(6, "рабы", false, 0)
            {
                // Добывают полезные ресурсы
                Production = (Stratum group, Cell place) => { place.Settling.Sources += place.Minigs.Extract(group.Man, 1); }
            }
        };
    }

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
            protected set { _satisfaction = Math.Min(1f, value); }
        }
        public CraftOrder CurrentOrder;
        public int AdultedMen { get; protected set; }
        public int AdultedWomen { get; protected set; }

        public Army CallMilitary(Age age, Army military = null)
        {
            var strength = Called < 3 ? r.Next(Man / Called) : 0;
            if (strength == 0)
            {
                throw new Exception("Никто не откликнулся");
            }

            if (military == null)
            {
                military = new Army()
                {
                    Strength = strength,
                    Regular = false,
                    NextPayDay = 1,
                    Energy = 1.0f,
                    Formation = new War.Battle.Formation { }
                };
            }

            var side = (int)(Math.Floor(Math.Sqrt(strength + military.Strength)));
            // Как отряд будет сражаться:
            var formation = new War.Battle.Formation();
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

                military.Strength += strength;
                military.Class = militaryClass;
                military.Formation = formation;
            } else
            {
                Class.CallToMilitary(this, military);
            }           
            return military;
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
