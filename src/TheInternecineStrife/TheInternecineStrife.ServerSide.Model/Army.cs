/*
 * Created by SharpDevelop.
 * User: Dmitry
 * Date: 14.11.2020
 * Time: 18:18
 * 
 * To change this template use Tools | Options | Coding | Edit Standard Headers.
 */
using System;
using TheInternecineStrife.ServerSide.Model.War;
using TheInternecineStrife.ServerSide.Model.War.Battle;

namespace TheInternecineStrife.ServerSide.Model
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
