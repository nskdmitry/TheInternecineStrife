/*
 * Created by SharpDevelop.
 * User: Dmitry
 * Date: 03.12.2020
 * Time: 18:23
 * 
 * To change this template use Tools | Options | Coding | Edit Standard Headers.
 */
using System;

namespace TheInternecineStrife.ServerSide.Model.Fabrics
{
	/// <summary>
	/// Description of Production.
	/// </summary>
	public abstract class Production
	{
		public abstract void Product(int count, Treasury founds);
	}
}
