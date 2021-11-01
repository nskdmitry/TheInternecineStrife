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
    public class WeaponController : ControllerBase
    {
        private readonly IWeapon _allWeapons;

        public WeaponController(IWeapon dateset) => _allWeapons = dateset ?? throw new ArgumentNullException(nameof(dateset));

        [HttpGet("{id}")]
        public async Task<ActionResult<Weapon>> GetWeapon(int id)
        {
            return new ObjectResult(_allWeapons.Get(id));
        }

        [HttpGet]
        public async Task<ActionResult<List<Weapon>>> List()
        {
            return new ObjectResult(_allWeapons.Weapons);
        }
    }
}