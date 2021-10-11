using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public enum GoodClass { Money, Supplies, Worker, Source, Item, Mercenaries };
       
    public class Good
    {
    	public int Id { get; set; }
        public string Name { get; set; }
        public float Price { get; set; }
        public GoodClass Type { get; set; }
        public Object Associate { get; set; }

        public Good(int id, string name, float goldEq, GoodClass type, object assoc = null)
        {
        	Id = id;
            Name = name;
            Price = goldEq;
            Type = type;
            Associate = assoc;
        }
        
        // TODO Переписать под загрузку из JSON-файла
        static Good()
        {
        	Resources = new List<Good> {
        		new Good(0, "", 0f, GoodClass.Money),
        		// from Age.StoneAge
        		new Good( 1, "золото", 0f, GoodClass.Money),
        		new Good( 2, "мясо", 1.2f, GoodClass.Supplies),
        		new Good( 3, "раб-скот", 1.5f, GoodClass.Worker),
        		new Good( 4, "кремень", 0.3f, GoodClass.Source),
        		new Good( 5, "камень", 0.9f, GoodClass.Source),
        		new Good( 6, "каменный нож", 2.2f, GoodClass.Item, War.Weapon.Variants[3]),
        		new Good( 7, "шкура-плащ", 2.2f, GoodClass.Item),
        		new Good( 8, "каменный топор", 0.4f, GoodClass.Item, War.Weapon.Variants[6]),
        		new Good( 9, "копье с каменным наконечником", 1f, GoodClass.Item, War.Weapon.Variants[4]),
        		new Good(10, "задира", 2.5f, GoodClass.Mercenaries),
        		new Good(11, "охотник", 5f, GoodClass.Mercenaries),
        		new Good(12, "дерево", 0.3f, GoodClass.Source),
        		// from Age.Neolit
        		new Good(13, "хлеб", 1.2f, GoodClass.Supplies),
        		new Good(14, "раб-скот", 3f, GoodClass.Worker),
        		new Good(15, "лук", 4.4f, GoodClass.Item, War.Weapon.Variants[5]),
        		new Good(16, "стрелы", 1f, GoodClass.Item, War.Weapon.Variants[9]),
        		new Good(17, "плетеный щит", 2.2f, GoodClass.Item),
        		new Good(18, "мужчина", 10f, GoodClass.Mercenaries),
        		new Good(19, "конь", 20f, GoodClass.Item),
        		new Good(20, "конный лучник", 25f, GoodClass.Mercenaries),
        		// from Age.Bronze
        		new Good(21, "бронза", 6f, GoodClass.Source),
        		new Good(22, "дротики", 12f, GoodClass.Item),
        		new Good(23, "бронзовый щит", 12f, GoodClass.Item),
        		new Good(24, "копьё с бронзовым наконечником", 8f, GoodClass.Item),
        		new Good(25, "застрельщик", 18f, GoodClass.Mercenaries),
        		new Good(26, "конный застрельщик", 24f, GoodClass.Mercenaries),
        		new Good(27, "ополченец", 20f, GoodClass.Mercenaries),
        		new Good(28, "тканный доспех", 6f, GoodClass.Item),
        		new Good(29, "бронзовый доспех", 21f, GoodClass.Item),
        		new Good(30, "пикенёр", 32f, GoodClass.Mercenaries),
        		new Good(31, "раб-ремесленник", 10f, GoodClass.Worker),
        		new Good(32, "одалиска", 8f, GoodClass.Worker),
        		new Good(33, "меч", 10f, GoodClass.Item),
        		// from Age.IronAge
        		new Good(34, "железо", 5.3f, GoodClass.Source),
        		new Good(35, "железное копьё", 2.8f, GoodClass.Item),
        		new Good(36, "железный щит", 9.0f, GoodClass.Item),
        		new Good(37, "чешуя", 24f, GoodClass.Item),
        		new Good(38, "железный меч", 16f, GoodClass.Item),
        		new Good(39, "легкий конник", 25.0f, GoodClass.Mercenaries),
        		// from Age.MiddleAge
        		new Good(40, "крепостной", 5f, GoodClass.Worker),
        		new Good(41, "булат", 6.9f, GoodClass.Source),
        		new Good(42, "кольчуга", 18f, GoodClass.Item),
        		new Good(43, "раубиттер", 40f, GoodClass.Mercenaries)
        	};
        }

        public static List<Good> Resources;
    }
}
