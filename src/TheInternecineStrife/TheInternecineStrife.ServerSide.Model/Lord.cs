using System;
using System.Collections.Generic;

namespace TheInternecineStrife.ServerSide.Model
{
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
