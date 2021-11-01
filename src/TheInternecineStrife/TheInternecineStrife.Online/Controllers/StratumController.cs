using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.Online.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class StratumController : ControllerBase
    {
        private Interfaces.IStratum dataset;

        public StratumController(Interfaces.IStratum stratumSet)
        {
            dataset = stratumSet;
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Models.Stratum>> Get(int id)
        {
            return new ObjectResult(dataset.Get(id));
        }

        [HttpGet("population/{idPopulation}")]
        public async Task<ActionResult<IEnumerable<Models.Stratum>>> GetOf(int idPopulation)
        {
            return new ObjectResult(dataset.GetStratasOf(idPopulation));
        }

        [HttpPost]
        public async Task<ActionResult<Models.Stratum>> Post(Models.Stratum stratum)
        {
            return new ObjectResult(dataset.Put(stratum));
        }

        [HttpPatch]
        public async Task<ActionResult<Models.Stratum>> Update(Models.Stratum stratum)
        {
            return new ObjectResult(dataset.Update(stratum));
        }

        // Stratum classes

        [HttpGet("class/{idClass}")]
        public async Task<ActionResult<StratumClass>> GetClass(int idClass)
        {
            return new ObjectResult(dataset.GetClass(idClass));
        }

        [HttpGet("class")]
        public async Task<ActionResult<IEnumerable<StratumClass>>> Classes() => new ObjectResult(dataset.GetAllStratumClasses());
    }
}