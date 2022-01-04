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
        /// <summary>
        /// Учётная сила армии. Задает уровень зарплаты, военных и продовольственных запасов.
        /// </summary>
        public int Strong => Stacks.Sum(regiment => (int)regiment?.Contract.Nominal);
		public int Strength {
            get => Stacks.Sum(regiment => (int)regiment?.Strength);
            set {
                var dead = Strength - value;
                if (dead < 0)
                {
                    return;
                }
                var dice = new Random();
                var deadInDivision = dice.Next(dead);
                var i = 0;
                while (deadInDivision > 0)
                {
                    Stacks[i].Strength -= deadInDivision;
                    i = (i + 1) % Stacks.Length;
                }
            }
        }
		
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
