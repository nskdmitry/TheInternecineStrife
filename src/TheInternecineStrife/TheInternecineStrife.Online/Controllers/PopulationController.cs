using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace TheInternecineStrife.Online.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class PopulationController : ControllerBase
    {
        private Interfaces.IPopulations dataStore;
        private Interfaces.IStratum stratums;

        public PopulationController(Interfaces.IPopulations mockPop, Interfaces.IStratum mockStratum)
        {
            dataStore = mockPop;
            stratums = mockStratum;
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Models.Population>> Get(int id)
        {
            var population = dataStore.Get(id);
            if (population == null)
            {
                return new ObjectResult(population);
            }
            var strata = stratums.GetStratasOf(id).OrderBy(item => item.Class.Id);
            population.Nobility = strata.ElementAt(0) ?? population.Nobility;
            population.Merchantes = strata.ElementAt(1) ?? population.Merchantes;
            population.ArtistCraft = strata.ElementAt(2) ?? population.ArtistCraft;
            population.Clir = strata.ElementAt(3) ?? population.Clir;
            population.Freeman = strata.ElementAt(4) ?? population.Freeman;
            population.Serfs = strata.ElementAt(5) ?? population.Serfs;
            population.Slaves = strata.ElementAt(6) ?? population.Slaves;
            population = dataStore.Update(id, population);

            return new ObjectResult(population);
        }

        [HttpGet("at/{idCell}")]
        public async Task<ActionResult<Models.Population>> In(uint idCell)
        {
            var population = dataStore.Of(idCell);
            return await Get(population.Id);
        }

        [HttpPost]
        public async Task<ActionResult<Models.Population>> Add(Models.Population population)
        {
            var populo = dataStore.Put(population);
            stratums.Put(new Models.Stratum(0, populo.Id, populo.Nobility, 21));
            stratums.Put(new Models.Stratum(0, populo.Id, populo.Merchantes, 22));
            stratums.Put(new Models.Stratum(0, populo.Id, populo.ArtistCraft, 23));
            stratums.Put(new Models.Stratum(0, populo.Id, populo.Clir, 24));
            stratums.Put(new Models.Stratum(0, populo.Id, populo.Freeman, 25));
            stratums.Put(new Models.Stratum(0, populo.Id, populo.Serfs, 26));
            stratums.Put(new Models.Stratum(0, populo.Id, populo.Slaves, 27));
            return new ObjectResult(populo);
        }
    }
}