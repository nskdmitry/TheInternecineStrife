using System;
using System.Collections.Generic;

namespace TheInternecineStrife.ServerSide.Model
{
	public sealed class Epidemy
	{
		private static Random doom = new Random();

		public int ID { get; set; }
        public string Name { get; set; }
        public float Infectable { get; set; }
        public float DeathlyForSoldiers { get; set; }
        public float DeathlyForMan { get; set; }
        public float DeathlyForWoman { get; set; }
        public float DeathlyForKids { get; set; }
        public int LimitOfDead { get; set; }
        public int BasicLong { get; set; }

        public Epidemy(
            int id, string name, float infectable, int limit, int longest,
            float soldiers = 0, float man = 0, float feman = 0, float kids = 0
        )
        {
            ID = id;
            Name = name;
            Infectable = Math.Min(1, Math.Max(0.01f, infectable));
            LimitOfDead = limit;
            BasicLong = Math.Min(1, longest);
            float full = 0f;
            int nulls = 0;
            if (soldiers > 0) {
                full += soldiers;
                DeathlyForSoldiers = soldiers;
            } else nulls++;
            if (man > 0) {
                full += man;
                DeathlyForMan = man;
            } nulls++;
            if (feman > 0) {
                full += feman;
                DeathlyForWoman = feman;
            } else nulls++;
            if (kids > 0) {
                full += kids;
                DeathlyForKids = kids;
            } else nulls++;
            if (nulls == 0) return;

            float patrition = kids > 1.0 ? 0.25f : (1 - kids) / nulls;
            if (soldiers <= 0)
            {
                DeathlyForSoldiers = patrition;
            }
            if (man <= 0)
            {
                DeathlyForMan = patrition;
            }
            if (feman <= 0)
            {
                DeathlyForWoman = patrition;
            }
            if (kids <= 0)
            {
                DeathlyForKids = patrition;
            }
        }

        public Cell Apply(Cell place)
        {
            var powers = place.Camp;
            var populo = place.Population;
            var wholePopulationCount = powers.Strength + populo.Men + populo.Femen + populo.Childrens;
            
            var infectedSoldiers = powers.Strength > 0 ? powers.Strength * Infectable : 0;
            var infectedMan = populo.Men > 0 ? populo.Men * Infectable : 0;
            var infectedWoman = populo.Femen > 0 ? populo.Femen * Infectable : 0;
            var infectedChilds = populo.Childrens > 0 ? populo.Childrens * Infectable : 0;

            var deadSoldiers = doom.Next((int)Math.Floor(infectedSoldiers * DeathlyForSoldiers));
            var deadMan = doom.Next((int)Math.Floor(infectedMan * DeathlyForMan));
            var deadWoman = doom.Next((int)Math.Floor(infectedWoman * DeathlyForWoman));
            var deadKids = doom.Next((int)Math.Floor(infectedChilds * DeathlyForKids));
            var wholeDied = deadSoldiers + deadMan + deadWoman + deadKids;
            if (wholeDied > LimitOfDead)
            {
                deadSoldiers *= deadSoldiers / wholePopulationCount;
                deadMan *= deadMan / wholePopulationCount;
                deadWoman *= deadWoman / wholePopulationCount;
                deadKids *= deadKids / wholePopulationCount;
            }

            powers.Strength = Math.Max(powers.Strength - deadSoldiers, 0);
            populo.Death(deadMan, deadWoman, deadKids);
            return place;
        }

        public static Epidemy Never = new Epidemy(0, "(Не было)", 0, 0, 1, 1, 1, 1);

        public static Dictionary<string, Epidemy> Famous = new Dictionary<string, Epidemy>
        {
            {"Flue", new Epidemy(1, "Грипп", 0.2f, 1000, 2, 0.4f, 0.4f, 0.4f, 0.4f) },
            {"Influence", new Epidemy(2, "Простуда", 0.2f, 1000, 2, 0.2f, 0.2f, 0.2f, 0.4f) },
            {"Plague", new Epidemy(3, "Чума", 0.4f, 1000000, 5, 0.3f, 0.5f, 0.5f, 0.5f) },
            {"Smallpox", new Epidemy(4, "Оспа", 0.75f, 100000, 10, 0.7f, 0.7f, 0.7f, 0.7f) },
            {"Tuberculouses", new Epidemy(5, "Чахотка", 0.85f, 100000, 2, 0.5f, 0.5f, 0.7f, 0.8f) },
            {"Antrax", new Epidemy(6, "Сибирская язва", 0.6f, 100000, 100, 0.5f, 0.5f, 0.5f, 0.9f) },
            {"Measles", new Epidemy(7, "Корь", 0.9f, 10000, 10, 0.3f, 0.3f, 0.4f, 0.5f) },
            {"Varicella", new Epidemy(8, "Ветрянка", 0.7f, 100, 2, 0.1f, 0.1f, 0.1f) },
            {"Cholera", new Epidemy(9, "Холера", 0.4f, 1000000, 100, 0.5f, 0.5f, 0.5f, 0.3f) },
            {"Spanish flue", new Epidemy(10, "Испанский грипп", 0.5f, 1000000, 10) },
            {"Ebola", new Epidemy(11, "лихорадка Эбола", 0.05f, 1000, 3, 0.5f, 0.5f, 0.5f, 0.9f) },
            {"Malaria", new Epidemy(12, "Малярия", 0.7f, 1000000, 5) },
            {"Dysentery", new Epidemy(13, "Дизентерия", 0.2f, 100000, 5) },
            {"Typhos", new Epidemy(14, "Тиф", 0.4f, 1000000, 10) },
            {"Thrush", new Epidemy(15, "Кандидоз", 0.45f, 10000, 3) },
            {"Tetanus", new Epidemy(16, "Столбняк", 0.2f, 100, 3) },
            {"Meningitus", new Epidemy(17, "Менингит", 0.4f, 1000, 3) },
            {"Pertusis", new Epidemy(18, "Коклюш", 0.5f, 1000, 10) },
            {"Encephalitis", new Epidemy(19, "Энцифалит", 0.1f, 100, 3) },
            {"Erysipelas", new Epidemy(20, "Рожа", 0.2f, 10, 4, 0.05f, 0.05f, 0.05f, 0.75f) },
            {"Shingles", new Epidemy(21, "Полосующий лишай", 0.1f, 1000, 1, 0.1f, 0.1f, 0.1f, 0.01f) },
        };
	}
}
