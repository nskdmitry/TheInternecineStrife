using System.Collections.Generic;
using TheInternecineStrife.ServerSide.Model.Protocol;

namespace TheInternecineStrife.ServerSide.Model.War
{
    public enum BattleSide { Left = -1, Center = 0, Right = 1 };
    public enum BattleDepth { Avan = -1, Body = 0, Arier = 2 }; 
    public enum ContractClass { Military, Mercenary, Regulary };
    public enum StrongNominal { Subdivision=10, Hundred=100, Thousand=1000, Legion=10000 };

    /// <summary>
    /// Контракт, описывающий условия службы
    /// </summary>
    public struct Contract
    {
        public ContractClass Class { get; set; }
        public int Day { get; set; }
        public int Length { get; }
        public int Deadline { get; private set; }
        // Закончилось ли формирование отряда? 
        // Если да, его уже не пополнишь. Если не сформирован, то его не отправишь.
        public bool Formed
        {
            get { return _formed; }
            set { if (!_formed) _formed = value; }
        }
        /// <summary>
        /// Номинальная численность.
        /// По ней считаются потребности провизии, оружии. По ней же считается зарплата.
        /// Также именно по ним считается "наглядная" численность войск.
        /// </summary>
        public StrongNominal Nominal { get; set; }

        public Contract(ContractClass relation, StrongNominal size, int now, int contractDays)
        {
            Class = relation;
            Day = now;
            Length = contractDays;
            Deadline = now + contractDays;
            Nominal = size;
            _formed = false;
        }

        public void Prolong()
        {
            if (_formed) Deadline += Length;
        }

        private bool _formed;
    }

    /// <summary>
    /// Полк в составе армии. Может принадлежать кому угодно, не только тому, кто сформировал армию. Воевать может только в составе армии.
    /// </summary>
    public class Division : Controllable
    {
        public SoldierProfile Profile { get; protected set; } // Тип войск
        public Social.StratumClass Stracia { get; set; } // Могут собираться только из равных
        public int Strength { get; set; } = 0; // Численость
        public Contract Contract { get; set; } // Контракт, по которому дивизия и несёт службу
        public Controllable Home { get; protected set; } // Кто прислал войска, кто им платит и кому они на самом деле верны
        public Economic.Wagoon Baggage { get; } // Обоз

        /// <summary>
        /// Боевые качества
        /// </summary>
        public float Energy { get; set; } = 1; // Силы сражаться
        public Battle.Formation Formation { get; set; } // Строй
        public float Experience { get => exp; set { if (value > exp) exp = value; } }

        /// <summary>
        /// Положение отряда при развёртывании перед боем.
        /// </summary>
        public BattleSide FrontWing { get; set; } = BattleSide.Center; // Крыло
        public BattleDepth FrontDepth { get; set; }

        public Division(
            string title, 
            int gameDay, 
            Controllable coordinator, 
            SoldierProfile warclass, 
            ContractClass contract,
            StrongNominal force)
        {
            Name = title;
            Home = coordinator;
            Owner = coordinator.Owner;
            Strength = 0;
            Profile = warclass;
            Energy = 1.00f;
            Formation = new Battle.Formation() {
                Columns = 10,
                Rows = 20,
                Density = 3f,
                FireOnMarsh = false,
                MaleeAttackDistance = warclass.Malee.Far,
                MaleeResource = warclass.Malee?.Resource ?? 0,
                RetreetDistance = -20*3f,
                RangeAttackDistance = warclass.Range?.Far-2 ?? 0f,
                RangeResource = warclass.Range?.Resource ?? 0,
                Ranger = warclass.Range != null,
                NoBlendMalee = true
            };
            Contract = new Contract(contract, force, gameDay, 5);
            Baggage = new Economic.Wagoon()
            {
                Private = this,
            };
        }

        public float MaleePercision { get => 0.85f - 1/(exp + 2); }
        public float RangePercision { get => 1 - 1/(exp + 2); }
        public float OrderDeliverSpeed { get => 1 - 1000/(exp + 1000); }
        public float FormationUnoSpeed { get => OrderDeliverSpeed; }

        private float exp = 0;
    }
}