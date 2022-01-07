using System;
using System.Runtime.Serialization;
using TheInternecineStrife.ServerSide.Model.War;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.ServerSide.Model
{
    /// <summary>
    /// Подсветка (разведанность) клетки
    /// </summary>
    public enum Highlighting {
        Hidden =0, // Сокрыть клетку
        Terriain =1, // Известен тип местности
        Politics =2, // Известно, какой области принадлежит.
        Settlings =3, // Известно, есть ли поселение в клетке и чьё оно.
        Armies =4, // Известно о том, что есть/нет армия и чья она.
        Populations =5, // Известен состав населения клетки.
        Forces =6, // Известен состав армии.
        Full =7 // Клетка полностью подконтрольна игроку. Он знает о ней вообще всё!
    };

    public struct Point
    {
        public readonly int X;
        public readonly int Y;
        public Point(int x, int y)
        {
            X = x;
            Y = y;
        }
    }

	/// <summary>
	/// Игровая клетка.
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
        // Добыча ресурсов: сельское хозяйство, валка леса/добыча минералов, цех/посад.
        public Economic.OutwallProduction Production { get; private set; }
        public Highlighting Known { get; set; }
		
		public int Welfare { 
			get { return _welfare; } 
			set {
				if (value > WELFARE_AMPLITUDE) {
					_welfare = WELFARE_AMPLITUDE;
					return;
				}
				if (-value > WELFARE_AMPLITUDE) {
					_welfare = -WELFARE_AMPLITUDE;
				}
                _welfare = value;
			}
		}
		
		protected int _welfare = 0;
		
		void ISerializable.GetObjectData(SerializationInfo info, StreamingContext context)
		{
			throw new NotImplementedException();
		}
	}
}