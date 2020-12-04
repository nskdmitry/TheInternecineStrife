/*
 * Created by SharpDevelop.
 * User: Dmitry
 * Date: 14.11.2020
 * Time: 18:18
 * 
 * To change this template use Tools | Options | Coding | Edit Standard Headers.
 */
using System;

namespace TheInternecineStrife.ServerSide.Model
{
	/// <summary>
	/// Description of Army.
	/// </summary>
	public class Army
	{
		public int Id { get; set; }
		public int Strength { get; set; }
		public bool Regular { get; set; }
		public int NextPayDay { get; set; }
		
		
		public Army()
		{
		}
	}
}
