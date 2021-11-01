using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TheInternecineStrife.Online.Models;

namespace TheInternecineStrife.Online.Mocks
{
    public class MockTexturePack : Interfaces.ITexture
    {
        private List<TexturePack> _all = new List<TexturePack>(100);
        public MockTexturePack()
        {
            _all.Add(new TexturePack() { Id = 1, Path = "data/assets/textures/MainMenu.jpg" }.Load());
            _all.Add(new TexturePack() { Id = 2, Path = "data/assets/textures/banners.png" }.Load());
            _all.Add(new TexturePack() { Id = 3, Path = "data/assets/textures/landscapes/air.png" }.Load());
            _all.Add(new TexturePack() { Id = 4, Path = "data/assets/textures/landscapes/westland.png" }.Load());
            _all.Add(new TexturePack() { Id = 5, Path = "data/assets/textures/landscapes/fields.png" }.Load());
            _all.Add(new TexturePack() { Id = 6, Path = "data/assets/textures/landscapes/sands.png" }.Load());
            _all.Add(new TexturePack() { Id = 7, Path = "data/assets/textures/landscapes/hills.png" }.Load());
            _all.Add(new TexturePack() { Id = 8, Path = "data/assets/textures/landscapes/forest.png" }.Load());
            _all.Add(new TexturePack() { Id = 9, Path = "data/assets/textures/landscapes/lake.png" }.Load());
            _all.Add(new TexturePack() { Id = 10, Path = "data/assets/textures/landscapes/brick_.png" }.Load());
        }

        public List<TexturePack> Textures => throw new NotImplementedException();

        public TexturePack Get(int id)
        {
            throw new NotImplementedException();
        }
    }
}
