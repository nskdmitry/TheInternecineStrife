using System;
using System.Collections.Generic;
using System.Linq;
using TheInternecineStrife.ServerSide.Model.War.Battle;

namespace TheInternecineStrife.ServerSide.Model.War
{
	/// <summary>
	/// Description of Army.
	/// </summary>
	public class Army : Protocol.Controllable
	{
        // Отряды, составляющие армию. Они не могу смешиваться между собой, но могут быть расформированы или покинуть армию в любой момент.
        public Division[] Stacks = new Division[9];

		public int Strength { get; set; }
		public bool Regular { get; set; }
		public int NextPayDay { get; set; }
		
        public float Energy { get; set; }
        public SoldierProfile Class { get; set; }
        public Formation Formation { get; set; }
		
		public Army()
		{
		}

        public bool Include(Division regiment)
        {
            int free = -1;
            for(int i = 0; i<9; i++)
            {
                if (Stacks[i] == null)
                {
                    free = i;
                    break;
                }
            }
            if (free == -1)
            {
                return false;
            }
            Stacks[free] = regiment;
            return true;
        }
	}
}
