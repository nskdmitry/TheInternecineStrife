using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using TheInternecineStrife.Online.Models;

namespace TheInternecineStrife.Online.Mocks
{
    public class MockPopulations : Interfaces.IPopulations
    {
        private readonly List<Population> populations = new List<Population>(100);

        public Population Get(int id)
        {
            return populations.First(item => item.Id == id);
        }

        public Population Of(uint idPlace)
        {
            return populations.First(item => item.PlaceId == idPlace);
        }

        public Population Put(Population population)
        {
            if (populations.Any(populo => populo.PlaceId == population.PlaceId))
            {
                throw new ArgumentException("Это место уже населено");
            }
            population.Id = populations.Count;
            populations.Add(population);
            return population;
        }

        public Population Update(int id, Population population)
        {
            var prev = populations.First(item => item.Id == population.Id);
            var index = populations.IndexOf(prev);
            populations.RemoveAt(index);
            population.Id = id;
            population.PlaceId = prev.PlaceId;
            populations.Insert(index, population);
            return population;
        }
    }
}
