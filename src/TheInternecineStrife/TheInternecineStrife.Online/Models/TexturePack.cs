using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TheInternecineStrife.Online.Models
{
    /// <summary>
    /// Текстуры чего угодно.
    /// </summary>
    public class TexturePack
    {
        public int Id { get; set; }
        public string Path { get; set; }
        public byte[] Content { get; private set; }
        public bool Loaded { get; private set; } = false;

        public TexturePack Load()
        {
            //Content = new byte[1024];
            //Loaded = false;
            return this;
        }
    }
}
