using System;

namespace TheInternecineStrife.ServerSide.Model.War
{
	public enum MarshAtLine { Up=-1, Stop=0, Down=1 };
	public enum WeaponClass { Malee=1, Range=2, Siege=3};
	
	/// <summary>
	/// Marsh command for warrior formation.
	/// </summary>
	public class FormationVector
	{
		public MarshAtLine Direction = MarshAtLine.Stop;
		public WeaponClass AttackBy = WeaponClass.Malee;
		
		public FormationVector()
		{
		}
	}
}
