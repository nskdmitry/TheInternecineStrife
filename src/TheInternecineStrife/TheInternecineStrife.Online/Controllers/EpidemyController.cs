using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using TheInternecineStrife.Online.Interfaces;
using TheInternecineStrife.ServerSide.Model;

namespace TheInternecineStrife.Online.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class EpidemyController : ControllerBase
    {
        private readonly IEpidemy _source;

        public EpidemyController(IEpidemy dataset)
        {
            _source = dataset;
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Epidemy>> Get(int id) => new ObjectResult(_source.Epidemies.First(item => item.ID == id));

        [HttpGet]
        public async Task<ActionResult<List<Epidemy>>> List() => new ObjectResult(_source.Epidemies);
    }
}