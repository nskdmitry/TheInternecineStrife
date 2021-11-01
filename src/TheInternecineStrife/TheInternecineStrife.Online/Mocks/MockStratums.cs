using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.Online.Interfaces;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.Online.Mocks
{
    public class MockStratums : IStratum
    {
        private readonly List<Models.Stratum> allPopulationStratums = new List<Models.Stratum>(300);

        public IEnumerable<StratumClass> GetAllStratumClasses()
        {
            return StratumClass.Classes;
        }

        public StratumClass GetClass(int id)
        {
            return StratumClass.Classes[id - 1];
        }

        public Models.Stratum Get(int id)
        {
            return allPopulationStratums[id - 1];
        }

        public IEnumerable<Models.Stratum> GetStratasOf(int idPopulation)
        {
            return allPopulationStratums.Where(strata => strata.PopulationId == idPopulation);
        }

        public Models.Stratum Put(Models.Stratum stratum)
        {
            if (allPopulationStratums.Any(strata => strata.Class.Id == stratum.Class.Id 
            && strata.PopulationId == stratum.PopulationId))
            {
                throw new ArgumentException("Такое сословие в данной популяции уже есть");
            }
            stratum.Id = allPopulationStratums.Count;
            allPopulationStratums.Add(stratum);
            return stratum;
        }

        public Models.Stratum Update(Models.Stratum stratum)
        {
            var index = allPopulationStratums.IndexOf(allPopulationStratums.First(strata => stratum.Id == strata.Id));
            allPopulationStratums.RemoveAt(index);
            allPopulationStratums.Insert(index, stratum);
            return stratum;
        }
    }
}
