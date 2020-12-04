using System;

namespace TheInternecineStrife.ServerSide.Model
{
	public class Dwelling
	{
		public int Id { get; set; }
		public string Name { get; set; }
		
		public LandType Class { get; set; }
		public float Founds { get; set; }

		public float DensityWallMaterial { get; set; }
		public float WallsHeight { get; set; }
		public float WallsActualHeight { get; set; }
		public int WallsPerimeter {get; set; }
		
		public Army Guard { get; set; }
		public bool Opened { get; set; }
	}
}
