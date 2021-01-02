using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System.IO;

namespace TheInternecineStrife.ServerSide.Model
{
    /// <summary>
    /// Способ ведения деятельности в клетке
    /// </summary>
    public enum CellProfile { TaxOnly=0, WarOnly=1, War=2, Tax=3, Armory=4, Progress=5, Agrary=6 };

    /// <summary>
    /// Эпоха.
    /// </summary>
    public enum Age { StoneAge=0, Neolit=1, Bronze=2, IronAge=3, MiddleAge=4 };

    /// <summary>
    /// Тип местности
    /// </summary>
    public enum PlaceType { Air=0, Earth=1, Water=2, Bridge=3, Port=4 };

    public class LandType
    {
        public int Id { set; get; }
        public string Name { set; get; }
        public float Low { set; get; }
        public float High { set; get; }
        public bool Civilization { set; get; }
        public int Hobbitable { set; get; }
        public int Capacity { set; get; }
        public float YieldLimit { set; get; }
        public float YieldStart { set; get; }
        public float Cross {set; get; }
        public CellProfile Orient { set; get; }
        public PlaceType Envirounment { set; get; }
        public Age Level { set; get; }
        public float Comfort { get { return 1 - Cross; } }
        
        // TODO Это тоже надо как-то интегрировать с landscape.json
        /** TODO Что, если данные о стоимости терраформирования не хранить в типе данных,
         * а считать прямо перед созданием стройплощадки? Тогда она требовала бы следующие
         * данные: численность крестьян, состояние клетки, тип местности, высота местности,
         * целевой тип местности. Может, что ещё. Это упростило бы класс и формат landscape.json
         * Да, так и нужно сделать.
         **/

        protected LandType(
            int id, 
            string name, 
            int populationLimit,
            float taxLimit,
            float cross,
            bool civil = false,
            PlaceType place = PlaceType.Earth,
            CellProfile profile = CellProfile.WarOnly,
            Age level = Age.StoneAge
        )
        {
            Id = id;
            Name = name;
            YieldLimit = taxLimit;
            Envirounment = place;
            Orient = profile;
            Level = level;
            Cross = cross;

            Civilization = civil;
            Capacity = Math.Max(1000, populationLimit);
            switch (place)
            {
                case PlaceType.Air:
                case PlaceType.Water:
                case PlaceType.Bridge:
                    Hobbitable = 0;
                    break;
                case PlaceType.Earth:
                    Hobbitable = (1 + (civil ? 1 : 0)) * populationLimit / 2;
                    break;
                case PlaceType.Port:
                    Hobbitable = populationLimit;
                    break;
            }
        }

		public static float GetTraversable(Cell start, Cell end)
		{
			return Traversity[(int)start.Background.Envirounment, (int)end.Background.Envirounment];
		}

		protected static readonly float[,] Traversity = {
			// To {Air, Earth, Water, Bridge, Port}
			{1, 0, 0,    1,    0}, // From Air
			{0, 1, 0, 9/10, 9/10}, // From Earth
			{0, 0, 1,  1/2,    1}, // From Water
			{0, 1, 0,    1,    1}, // From Bridge
			{0, 1, 1,    1,    1}  // From Port
		};
		
		/// TODO Loading a Set from JSON statically.
		static LandType()
        {
            var path = Path.Combine(Path.GetFullPath(".."), "data", "basic", "landscape.json");
            if (File.Exists(path))
            {
                var content = File.ReadAllText(path);
                Set = JsonConvert.DeserializeObject<Dictionary<string, LandType>>(content);
                return;
            }
            Console.WriteLine(String.Format("Load from {}: file not found", path));
            Set =  new Dictionary<string, LandType>{
            	{"westland", new LandType(0, "пустошь", 1000, 0.030f, 0.25f, false, PlaceType.Earth, CellProfile.War, Age.StoneAge) },
            	{"fields", new LandType(1, "луг", 1000, 0.010f, 0.2f, false, PlaceType.Earth, CellProfile.TaxOnly, Age.StoneAge) },
            	{"desert", new LandType(2, "пустыня", 200, 0.1f, 0.2f, false, PlaceType.Earth, CellProfile.WarOnly, Age.StoneAge) },
            	{"hill", new LandType(3, "холм", 750, 0.250f, 0.5f, false, PlaceType.Earth, CellProfile.Tax, Age.StoneAge) },
            	{"forest", new LandType(4, "лес", 750, 0.2f, 0.75f, false, PlaceType.Earth, CellProfile.Tax, Age.StoneAge) },
            	{"lake", new LandType(5, "озеро", 0, 1.5f, 0.1f, false, PlaceType.Water, CellProfile.TaxOnly, Age.StoneAge) },
           	 	{"place", new LandType(100, "стройка", 1000, 0f, 0.2f, true, PlaceType.Earth, CellProfile.Progress, Age.StoneAge) },
           	 	{"outpost", new LandType(102, "застава", 50, -0.02f, 0.1f, true, PlaceType.Earth, CellProfile.WarOnly, Age.Neolit) },
            	{"camp", new LandType(101, "лагерь", 100, 0.1f, 0.1f, true, PlaceType.Earth, CellProfile.War, Age.Bronze) },
            	{"fort", new LandType(103, "острог", 500, 0.150f, 0.1f, true, PlaceType.Earth, CellProfile.War, Age.Bronze) },
            	{"castle", new LandType(104, "крепость", 800, 0f, 0.1f, true, PlaceType.Earth, CellProfile.War, Age.IronAge) },
            	{"cytadel", new LandType(105, "твердыня", 1000, -0.2f, 0.3f, true, PlaceType.Earth, CellProfile.War, Age.MiddleAge) },
            	{"town", new LandType(106, "посад", 30000, 5.1f, 0.3f, true, PlaceType.Earth, CellProfile.TaxOnly, Age.Bronze) },
            	{"field", new LandType(107, "нива", 300, 5.0f, 0.3f, true, PlaceType.Earth, CellProfile.TaxOnly, Age.Bronze) },
                {"harbour", new LandType(108, "гавань", 1500, 10f, 0.2f, true, PlaceType.Port, CellProfile.Progress, Age.Bronze) },
        	};
        }
		
        public static readonly Dictionary<string, LandType> Set;

        public static readonly LandType Default = Set["westland"];
    }
}
