using TheInternecineStrife.ServerSide.Model.Social;

namespace TheInternecineStrife.Online.Models
{
    public class Stratum : ServerSide.Model.Social.Stratum
    {
        public int Id { get; set; }
        public int PopulationId { get; set; }
        public int TextureId { get; set; }

        public Stratum(int id, int idPopulation, StratumClass socium, int idTexture) : base(socium)
        {
            Id = id;
            PopulationId = idPopulation;
            TextureId = idTexture;
        }

        public Stratum(int id, int idPopulation, ServerSide.Model.Social.Stratum stratum, int idTexture) : base(stratum.Class)
        {
            Id = id;
            PopulationId = idPopulation;
            TextureId = idTexture;

            Satisfaction = stratum.Satisfaction;
            CurrentOrder = stratum.CurrentOrder;
            Called = stratum.Called;
            AdultedMen = stratum.AdultedMen;
            AdultedWomen = stratum.AdultedWomen;
        }
    }
}
