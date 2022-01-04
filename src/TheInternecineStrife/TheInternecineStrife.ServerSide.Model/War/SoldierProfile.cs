using System;
using System.Collections.Generic;
using TheInternecineStrife.ServerSide.Model.Economic;
//using Newtonsoft.Json;
using System.Linq;
using System.Text;
using System.IO;

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
        public bool Machined { protected set; get; }
        public readonly PriceOf Price;

        public const float HAVY_MARSH_SPEED = 4.0f;
        public const float LIGHT_RUN_SPEED = 10.0f;
        public const float CHARIOT_SPEED = 24.0f;
        public const float LIGHT_HORSE_SPEED = 36;
        public const float KNIGHT_HORSE_SPEED = 21;
        
        public static List<SoldierProfile> Basic = new List<SoldierProfile>(20);

        static SoldierProfile()
        {
            var path = Path.Combine(Path.GetFullPath(".."), "data", "basic", "soldiers.json"); ;
            if (File.Exists(path))
            {
                //var content = File.ReadAllText(path);
                //Basic.AddRange(JsonConvert.DeserializeObject<SoldierProfile[]>(content));
            }
        }

        /// <summary>
        /// Подсчет того, насколько далеко может выстрелить солдат данного рода войск.
        /// Пояснение: осадные машины и арбалеты могут не зависеть от усталости солдат.
        /// </summary>
        /// <param name="heightDifference">Разница высот между данным подразделением и его целью.</param>
        /// <param name="energy">Сколько осталось сил. Лучники имеют свойство уставать.</param>
        /// <returns>Максимальная дальность.</returns>
       public float GetRangeLimit(float heightDifference, float energy)
        {
            energy = Math.Min(1.0f, energy);
            var highBonus = CalcRangeDistanceBonus(heightDifference);
            return highBonus + (!Machined ? (energy * (Range.Far - Range.Near)) + Range.Near : Range.Far);
        }

        /// <summary>
        /// Подсчет того, как высота влияет на дальность.
        /// </summary>
        /// <param name="distanceDifference">Разница высот</param>
        /// <returns></returns>
        protected float CalcRangeDistanceBonus(float distanceDifference)
        {
            if (distanceDifference == 0)
            {
                return distanceDifference;
            }
            return (float)(Math.Sqrt(Math.Abs(distanceDifference)) * Math.Sign(distanceDifference));
        }
    }
}
