using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.War
{
    public class Weapon
    {
    	public int Id { get; set; }
    	public string Name { get; set; }
        public float Damage { get; set; }
        public float Near { get; set; }
        public float Far { get; set; }
        public int Resource { get; set; }
        
        public static Weapon[] Variants = new Weapon[] {
            new Weapon() {Id=0, Name="кулаки", Damage=1, Far=1f, Near=0.5f },
            new Weapon() {Id=1, Name="праща", Damage=2.5f, Far=6, Near=0.5f },
            new Weapon() {Id=2, Name="копьё", Damage=5f, Far=10f, Near=2f },
            new Weapon() {Id=3, Name="простой лук", Damage=2f, Far=50f, Near=5f },
            new Weapon() {Id=4, Name="булава", Damage=7f, Far=2, Near=1f },
            new Weapon() {Id=5, Name="пика", Damage=7f, Far=4f, Near=2f },
            new Weapon() {Id=6, Name="рогатый лук", Damage=2f, Far=80f, Near=3f },
            new Weapon() {Id=7, Name="дротики", Damage=7f, Far=10f, Near=1f},
            new Weapon() {Id=8, Name="кавалерийская пика", Damage=10f, Far=3f, Near=2f}
        };
    }
}
