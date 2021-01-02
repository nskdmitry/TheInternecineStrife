using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.War
{
    public class SoldierProfile
    {
    	public int Id;
    	public string Name;
    	public Age From;
        public float Health;
        public float Speed;
        public Weapon Malee;
        public Weapon Range;
        
        public GoodItem[] Property;
        
        public static List<SoldierProfile> Basic = new List<SoldierProfile>{
        	new SoldierProfile { 
        		Id=1, 
        		Name="Застрельщик", 
        		From= Age.StoneAge, 
        		Health=10, Speed=0.5f,
        		Property= new GoodItem[] {
        			new GoodItem { Type=Good.Resources[9], Amount=3},
        			new GoodItem { Type=Good.Resources[7], Amount=1 },
        			new GoodItem { Type=Good.Resources[1], Amount=0.2f }
        		},
        		Malee = null,
        		Range = null
        	},
        	new SoldierProfile {
        		Id=2,
        		Name="Пращник",
        		From= Age.StoneAge,
        		Health=10, Speed=0.5f,
        		Property = new GoodItem[]{
        			new GoodItem { Type=Good.Resources[4], Amount=10 },
        			new GoodItem { Type=Good.Resources[1], Amount=0.15f }
        		},
        		Malee=null,
        		Range=null
        	},
        	new SoldierProfile {
        		Id=3,
        		Name="Булавщик",
        		From=Age.StoneAge,
        		Health=10, Speed=0.5f,
        		Property= new GoodItem[]{
        			new GoodItem{ Type=Good.Resources[7], Amount=1, },
        			new GoodItem{ Type=Good.Resources[1], Amount=0.1f },
        			new GoodItem{ Type=Good.Resources[12], Amount=0.1f}
        		},
        		Malee=null,
        		Range=null
        	},
        	new SoldierProfile {
        		Id=4,
        		Name="Рубака с топором",
        		From= Age.StoneAge,
        		Health=10, Speed=0.5f,
        		Property= new GoodItem[] {
        			new GoodItem{ Type=Good.Resources[7], Amount=1 },
        			new GoodItem{ Type=Good.Resources[4], Amount=2 },
        			new GoodItem{ Type=Good.Resources[1], Amount=3 }
        		},
        		Malee=null,
        		Range=null
        	},
        	new SoldierProfile {
        		Id=5,
        		Name="Лёгкий копейщик",
        		From= Age.StoneAge,
        		Health=10, Speed=0.5f,
        		Property= new GoodItem[] {
        			new GoodItem{ Type=Good.Resources[17], Amount=1 },
        			new GoodItem{ Type=Good.Resources[9], Amount=1 },
        			new GoodItem{ Type=Good.Resources[8], Amount=1 },
        			new GoodItem{ Type=Good.Resources[1], Amount=0.3f }
        		},
        		Malee=null,
        		Range=null
        	},
        	new SoldierProfile {
				Id=6,
				Name="Копейщик в кожанной броне",
				From= Age.StoneAge,
				Health=10, Speed=0.4f,
				Property = new GoodItem[] {
					new GoodItem{ Type=Good.Resources[17], Amount=1 },
					new GoodItem{ Type=Good.Resources[9], Amount=1},
					new GoodItem{ Type=Good.Resources[7], Amount=4},
					new GoodItem{ Type=Good.Resources[6], Amount=1},
					new GoodItem{ Type=Good.Resources[2], Amount=2},
					new GoodItem{ Type=Good.Resources[1], Amount=1}
				},
				Malee=null,
				Range=null
        	}
        };
    }
}
