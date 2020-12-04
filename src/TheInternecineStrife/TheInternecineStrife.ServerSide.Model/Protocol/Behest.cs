using System;

namespace TheInternecineStrife.ServerSide.Model.Protocol
{
	public enum BehestContentCategory { Marsh=1, Disband=2, Recruit=3, TransferControl=4 };
	
	/// <summary>
	/// Приказ - общая 
	/// </summary>
	public class Behest
	{
		public int Id { get; set; }
		public int IdLordSender { get; set; }
		public int IdLordReceiver { get; set; }
		public int IdArmyReceiver { get; set; }
		public int IdTargetPlace { get; set; }
		public int OrderVolume { get; set; }
		public BehestContentCategory Class { get; set; }
		
		public Behest()
		{
			Class = BehestContentCategory.Marsh;
		}
	}
}
