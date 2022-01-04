using System;

namespace TheInternecineStrife.ServerSide.Model.War
{
	/// <summary>
	/// Using at attack for fortess. It destroys walls.
	/// </summary>
	public class SiegeMachine : SoldierProfile
	{
		public int Count {get; set; }
		public int Integrity { get; set; }
		public float Damage { get; set; }
		
		public SiegeMachine()
		{
            Machined = true;
		}
	}
}
