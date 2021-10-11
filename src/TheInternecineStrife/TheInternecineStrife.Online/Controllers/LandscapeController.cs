using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using TheInternecineStrife.Online.Interfaces;
using TheInternecineStrife.Online.Models;

namespace TheInternecineStrife.Online.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class LandscapeController : ControllerBase
    {
        private readonly ILandscapes _allLandscapes;

        public LandscapeController(ILandscapes landscapeSet) => _allLandscapes = landscapeSet;

        [HttpGet("{id}")]
        public async Task<ActionResult<Landscape>> GetLandscape(int id)
        {
            var content = _allLandscapes.GetLandscape(id);
            return new ObjectResult(content);
        }

        [HttpGet]
        public async Task<ActionResult<List<Landscape>>> List()
        {
            var content = _allLandscapes.Landscapes;
            return new ObjectResult(content);
        }
    }
}