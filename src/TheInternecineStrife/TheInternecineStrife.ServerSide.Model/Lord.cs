using System;
using System.Collections.Generic;

namespace TheInternecineStrife.ServerSide.Model
{
	/// <summary>
	/// Description of Lord.
	/// </summary>
	public class Lord
	{
		public int Id { get; set; }
		public string Name { get; set; }
		public int idMainDomain { get; set; }
		public bool Active { get; set; }
		public List<Army> Forces { get; set; }
		
		public Lord()
		{
		}
	}
}
