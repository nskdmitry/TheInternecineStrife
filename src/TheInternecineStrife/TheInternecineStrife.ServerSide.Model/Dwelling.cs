using System;

namespace TheInternecineStrife.ServerSide.Model
{
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
	
	public class Dwelling
	{
		public int Id { get; set; }
		public string Name { get; set; }
		
		public LandType Class { get; set; }
		public float Founds { get; set; }

		public Material DensityWallMaterial { get; set; }
		public float WallsHeight { get; set; }
		public float WallsActualHeight { get; set; }
		public int WallsPerimeter {get; set; }
		
		public Army Guard { get; set; }
		public bool Opened { get; set; }
	}
}
