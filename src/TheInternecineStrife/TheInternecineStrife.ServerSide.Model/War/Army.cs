using System;
using TheInternecineStrife.ServerSide.Model.War.Battle;

namespace TheInternecineStrife.ServerSide.Model.War
{
	/// <summary>
	/// Description of Army.
	/// </summary>
	public class Army : Protocol.Controllable
	{
		public int Strength { get; set; }
		public bool Regular { get; set; }
		public int NextPayDay { get; set; }
		
        public float Energy { get; set; }
        public SoldierProfile Class { get; set; }
        public Formation Formation { get; set; }
		
		public Army()
		{
		}
	}
}
