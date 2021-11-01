using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.Online.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class SoldiersController : ControllerBase
    {
        private Interfaces.ISoldierProfile source;

        public SoldiersController(Interfaces.ISoldierProfile datasource)
        {
            source = datasource;
        }

        [HttpGet("classes")]
        public async Task<ActionResult<List<SoldierProfile>>> Soldiers() => new ObjectResult(source.List.Where(item => !item.Machined));

        [HttpGet("machines")]
        public async Task<ActionResult<List<SoldierProfile>>> Machines() => new ObjectResult(source.List.Where(item => item.Machined));

        [HttpGet("warclass/{id}")]
        public async Task<ActionResult<SoldierProfile>> Get(uint id) => new ObjectResult(source.Get(id));

        [HttpPut]
        public async Task<ActionResult<int>> Add(HttpRequest request)
        {
            var id = source.List.Count + 1;

            return new ObjectResult(id);
        }
    }
}