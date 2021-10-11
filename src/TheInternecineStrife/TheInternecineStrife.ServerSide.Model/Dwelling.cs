using System;
using TheInternecineStrife.ServerSide.Model.Economic;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.ServerSide.Model
{
    /// <summary>
    /// Матерьял - то, из чего строят стены. Имеют определённую плотность (под этим понимается стойкость к разрушению) и являются товаром.
    /// </summary>
	public struct Material
	{
		public int Id;
		public float Density;
		public Good Type;
		
		public Material(int id, Good source, float density)
		{
			Id = id;
			Density = density;
			Type = source;
		}
		
		public static Material[] Materials = {
			new Material(1, Good.Resources[12], 0.9f),
			new Material(2, Good.Resources[4], 3.9f),
			
		};
	}
	
    /// <summary>
    /// Укрепления.
    /// </summary>
    public struct WallOptions
    {
        public Material Material;
        public float Height;
        public float Perimeter;
        public float ActualHeight;
        public float Thickness;

        public WallOptions(Material material, float p, float h)
        {
            Thickness = 2;
            Material = material;
            Perimeter = p;
            Height = h;
            ActualHeight = h;
        }

        public float Volume { get { return Thickness * (Perimeter * Height - Height + ActualHeight); } }
        public float RepairVolume { get { return Thickness * (Height - ActualHeight) * Perimeter / 4; } }

        public static WallOptions None = new WallOptions(Material.Materials[0], 0, 0);
    }

    /// <summary>
    /// Поселение - место обитания населения клетки.
    /// Является антропоморфной местностью (параметр Class), местом сбора ресурсов (Founds), а также опорным пунктом (стены + Guard).
    /// Также является отправителем-получателем писем.
    /// </summary>
	public class Dwelling : Protocol.Controllable
    {		
		public LandType Class { get; set; }
		public float Founds { get; set; }
        public float Sources { get; set; }

        public WallOptions Walls;

		public Army Guard { get; set; }
		public bool Opened { get; set; }
	}
}
