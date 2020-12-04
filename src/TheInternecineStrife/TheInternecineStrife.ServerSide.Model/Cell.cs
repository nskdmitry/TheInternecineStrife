using System;
using System.Runtime.Serialization;
using System.Collections.Generic;

namespace TheInternecineStrife.ServerSide.Model
{	
	/// <summary>
	/// 
	/// </summary>
	public class Cell : ISerializable
	{
		protected int WELFARE_AMPLITUDE = 5;
		protected static int CELL_FACE_WIDHT = 1000;
		
		public int Id { get; set; }
		public int X { get; set; }
		public int Y { get; set; }
		public int Height { get; set; } // Height of center of cell
		
		public Population Population;
		public Army Camp { get; set; }
		public LandType Background { get; set; }
		public Dwelling Settling { get; set; }
		
		public int Welfare { 
			get { return _welfare; } 
			set {
				if (value > 0 && value > WELFARE_AMPLITUDE) {
					_welfare = WELFARE_AMPLITUDE;
					return;
				}
				if (value < 0 && -value > WELFARE_AMPLITUDE) {
					_welfare = -WELFARE_AMPLITUDE;
				}
			}
		}
		
		protected int _welfare = 0;
		
		void ISerializable.GetObjectData(SerializationInfo info, StreamingContext context)
		{
			throw new NotImplementedException();
		}
	}
}