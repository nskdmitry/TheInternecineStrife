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
            new Weapon() {Id=0, Name="кулаки", Damage=1, Far=1f, Near=0.5f },
        	new Weapon() {Id=1, Name="палка", Damage=2, Far=2, Near=1 },
            new Weapon() {Id=2, Name="камень", Damage=2.5f, Far=6, Near=0.5f },
            new Weapon() {Id=3, Name="каменный нож", Damage=4f, Far=1.2f, Near=0.5f },
            new Weapon() {Id=4, Name="копьё", Damage=5f, Far=10f, Near=2f },
            new Weapon() {Id=5, Name="простой лук", Damage=5f, Far=50f, Near=5f },
            new Weapon() {Id=6, Name="каменный топор", Damage=5f, Far=4f, Near=1f },
            new Weapon() {Id=7, Name="праща", Damage=6f, Far=21f, Near=5f },
            new Weapon() {Id=8, Name="ядро" },
            new Weapon() {Id=9, Name="стрела" },
            new Weapon() {Id=10, Name="булава", Damage=8, Far=2, Near=1f },
            new Weapon() {Id=11, Name="пика", Damage=6f, Far=4f, Near=2f },
            new Weapon() {Id=12, Name="рогатый лук", Damage=8f, Far=80f, Near=3f }
        };
    }
}
