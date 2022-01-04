using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public enum Wounding { Slight = 1, Moderate = 2, Hard = 3, Predeath = 4 };

    /// <summary>
    /// Обоз
    /// </summary>
    public class Wagoon : Treasury
    {
        // Рабы. Сюда попадают угнанные жители и военнопленные
        public Social.Stratum Slaves = new Social.Stratum(Social.StratumClass.Classes[6]);
        // Чей обоз
        public Division Private { get; set; }
        // Полковой госпиталь
        public Dictionary<Wounding, int> Lathareth { get;  } = new Dictionary<Wounding, int>();
    }
}
