using System.Collections.Generic;
using TheInternecineStrife.ServerSide.Model;

namespace TheInternecineStrife.Online.Mocks
{
    public class MockEpidemies : Interfaces.IEpidemy
    {
        private readonly List<Epidemy> _epidemies = new List<Epidemy>(10);

        public MockEpidemies()
        {
            _epidemies.Add(Epidemy.Never);
            foreach (var ill in Epidemy.Famous.Values)
            {
                _epidemies.Add(ill);
            }
        }

        public IList<Epidemy> Epidemies => _epidemies;
        public Epidemy Get(int id) => _epidemies[id];
    }
}
