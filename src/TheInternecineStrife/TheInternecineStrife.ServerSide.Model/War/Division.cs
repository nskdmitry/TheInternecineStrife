using System.Collections.Generic;

namespace TheInternecineStrife.ServerSide.Model.War
{
    public enum BattleSide { Left = -1, Center = 0, Right = 1 };

    /// <summary>
    /// Полк в составе армии. Может принадлежать кому угодно, не только тому, кто сформировал армию. Воевать может только в составе армии.
    /// </summary>
    public class Division : Protocol.Controllable
    {
        public SoldierProfile Profile { get; protected set; } // Тип войск
        public int Strength { get; set; } = 0; // Численость
        public float Energy { get; protected set; } = 1; // Силы сражаться
        public Battle.Formation Formation { get; set; } // Строй
        public bool Regular { get; set; } = false; // Расформировать по достижению NextPayDay
        public int NextPayDay { get; set; } // Дата получки или авторасформирования войск.
        public Cell Sender { get; protected set; } // Кто прислал войска, кто им платит и кому они на самом деле верны
        public BattleSide FrontWing { get; set; } = BattleSide.Center; // Крыло

        public Division(string title, int gameDay, Cell coordinator, SoldierProfile warclass, bool regular = false)
        {
            Name = title;
            Sender = coordinator;
            Owner = coordinator.Settling.Owner;
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
                NoBlendMalee = true,
                Woundeds = new List<int>(),
                Medics = 0
            };
            Regular = regular;
            NextPayDay = gameDay + 5;
        }
    }
}