using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

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
        public float Fortifiedness { set; get; }
        public CellProfile Orient { set; get; }
        public PlaceType Envirounment { set; get; }
        public Age Level { set; get; }
        public float Comfort { set; get; }
        public float TaxLimit { set; get; }
        public int PopulationLimit { set; get; }
        
        // TODO Это тоже надо как-то интегрировать с landscape.json
        /** TODO Что, если данные о стоимости терраформирования не хранить в типе данных,
         * а считать прямо перед созданием стройплощадки? Тогда она требовала бы следующие
         * данные: численность крестьян, состояние клетки, тип местности, высота местности,
         * целевой тип местности. Может, что ещё. Это упростило бы класс и формат landscape.json
         * Да, так и нужно сделать.
         **/
        public float TransportFatigue { set; get; }

        protected LandType(
            int id, 
            string name, 
            int populationLimit, 
            float taxLimit, 
            float defence,
            bool civil = false,
            float fatigue = 1,
            PlaceType place = PlaceType.Earth,
            CellProfile profile = CellProfile.WarOnly,
            Age level = Age.StoneAge,
            float comfort = 1.0f
        )
        {
            Id = id;
            Name = name;
            YieldLimit = taxLimit;
            Envirounment = place;
            Orient = profile;
            Level = level;
            
            PopulationLimit = populationLimit;
            TaxLimit = taxLimit;
            Fortifiedness = defence;
            TransportFatigue = fatigue;

            Civilization = civil;
            Capacity = Math.Max(1000, populationLimit);
            Comfort = Math.Min(1.0f, Math.Max(0f, comfort));
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

		protected static readonly float[,] Traversity = new float[5, 5]{
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
			Set =  new Dictionary<string, LandType>{
            	{"westland",
                	new LandType(0, "пустошь", 
                    	1000, 
                    	0.5f, 
                    	0.000f,
                    	false,
                    	1,
                    	PlaceType.Earth,
                    	CellProfile.WarOnly,
                    	Age.StoneAge,
                    	0.2f
                	)
            	},
            	{"fields",
                	new LandType(1, "луг", 
                	    1000, 
                	    2.5f, 
                	    0.010f,
                	    false,
                	    1,
                	    PlaceType.Earth,
                	    CellProfile.TaxOnly,
                	    Age.StoneAge,
                	    0.5f
                	)
            	},
            	{"desert",
                	new LandType(2, "пустыня", 
                	    200,
                	    0.1f, 
                	    0.0000f,
                	    false,
                	    1,
                	    PlaceType.Earth,
                	    CellProfile.WarOnly,
                	    Age.StoneAge,
                	    0.2f
                	)
            	},
            	{"hill",
                	new LandType(3, "холм", 
                	    750, 
                	    1.0f, 
                	    0.150f,
                	    false,
                	    1,
                	    PlaceType.Earth,
                	    CellProfile.Tax,
                	    Age.StoneAge,
                	    0.5f
                	)
            	},
            	{"forest",
                	new LandType(4, "лес", 
                	    750, 
                	    1.2f, 
                	    0.100f,
                	    false,
                	    1,
                	    PlaceType.Earth,
                	    CellProfile.Tax,
                	    Age.StoneAge,
                	    0.4f
                	)
            	},
            	{"lake",
                	new LandType(5, "озеро", 
                	    0, 
                	    0, 
                	    0, 
                	    false, 
                	    1.0f, 
                	    PlaceType.Water,
                	    CellProfile.TaxOnly,
                	    Age.StoneAge,
                	    1f
                	)
            	},
           	 	{"place",
           	    	 new LandType(100, "Срыть укрепления", 
                	    1000, 
           	    	     0.5f, 
           	    	     0.0000f, 
           	    	     true,
           	    	     1f,
           	    	     PlaceType.Earth,
           	    	     CellProfile.War,
           	    	     Age.Neolit,
           	    	     0.5f
           	    	)
           	 	},
           	 	{"outpost",
           	    	 new LandType(102, "Острог", 
                	    450, 
                	    0.005f, 
                	    0.190f,
                	    true,
                	    1,
                	    PlaceType.Earth,
                	    CellProfile.War,
                	    Age.Neolit,
                	    0.6f
                	)
            	},
            	{"camp",
                	new LandType(101, "Лагерь", 
                	    500, 
                	    0f, 
                	    0.210f,
                	    true,
                	    1,
                	    PlaceType.Earth,
                	    CellProfile.War,
                	    Age.Bronze
                	)
            	},
            	{"fort",
                	new LandType(103, "Застава", 
                	    500, 
                	    0f, 
                	    0.250f,
                	    true,
                	    1,
                	    PlaceType.Earth,
                	    CellProfile.Tax,
                	    Age.Bronze,
                	    0.7f
                	)
            	},
            	{"castle",
                	new LandType(104, "Крепость", 
                	    800, 
                	    0f, 
                	    0.333f,  
                	    true,
                	    1,
                	    PlaceType.Earth,
                	    CellProfile.War,
                	    Age.Bronze,
                	    1
                	)
            	},
            	{"cytadel",
                new LandType(105, "Твердыня", 
                    1000, 
                    0f, 
                    0.450f,  
                    true,
                    1,
                    PlaceType.Earth,
                    CellProfile.War,
                    Age.MiddleAge,
                    1
                )
            	},
            	{"town",
                new LandType(106, "Посад",
                    3000,
                    3.1f,
                    0.3f,
                    true,
                    1,
                    PlaceType.Earth,
                    CellProfile.TaxOnly,
                    Age.Bronze,
                    1
                )},
            	{"field",
                new LandType(107, "Нива",
                    300,
                    5.0f,
                    0.0f,
                    true,
                    1,
                    PlaceType.Earth,
                    CellProfile.TaxOnly,
                    Age.Bronze,
                    0.4f
                )},
        	};
		}
		
        public static readonly Dictionary<string, LandType> Set;

        public static readonly LandType Default = Set["westland"];
    }
}
