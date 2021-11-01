using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.Online.Models;

namespace TheInternecineStrife.Online.Interfaces
{
    interface ITexture
    {
        List<TexturePack> Textures { get; }
        TexturePack Get(int id);
    }
}
