using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model.Economic
{
    public class Resource
    {
        public readonly int Id;
        public readonly string Name;
        public readonly float Density;
        
        public Resource(int id, string name, float density)
        {
            Id = id;
            Name = name;
            Density = density;
        }

        public static Resource[] Available;
        // TODO Загружать из JSON-файла.
        static Resource()
        {
            Available = new Resource[] {

            };
        }
    }

    /// <summary>
    /// Место добычи ресурсов
    /// </summary>
    public sealed class Extraction
    {
        public readonly Resource Goods;
        public readonly float Amount;
        public readonly float Profit;
        public readonly int Wide;
        public bool Opened = false;

        public float Available { get; private set; }

        public float CurrentProfit(float instrument)
        {
            return (float)(Math.Min(Profit, instrument) * Available / Amount);
        }

        public float Extract(int workers, float instrument)
        {
            var sum = Math.Min(Available, CurrentProfit(instrument) * Math.Min(workers, Wide));
            Available -= sum;
            return sum;
        }
    }
}
