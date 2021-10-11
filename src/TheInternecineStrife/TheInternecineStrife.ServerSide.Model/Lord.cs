using System;
using System.Collections.Generic;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.ServerSide.Model
{
    public struct Technologies
    {
        public Age Epoch;
        public float ExtractKoeff;
    }

	/// <summary>
	/// Description of Lord.
	/// </summary>
	public class Lord : Protocol.Controllable
	{
		public int idMainDomain { get; set; }
		public List<Army> Forces { get; set; }
		
		public Lord()
		{
		}
	}
}
