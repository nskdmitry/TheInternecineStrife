using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.War
{
    public class Weapon
    {
    	public int Id;
    	public string Name;
        public float Damage;
        public float Near;
        public float Far;
        
        public static Weapon[] Variants = new Weapon[] {
        	
        };
    }
}
