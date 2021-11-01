namespace TheInternecineStrife.Online.Models
{
    public class Population : ServerSide.Model.Social.Population
    {
        public int Id { get; set; }
        public uint PlaceId { get; set; }

        public Population(int id, uint idPlace, ServerSide.Model.Social.Population population) : base()
        {
            Id = id;
            PlaceId = idPlace;
            Merchantes = population?.Merchantes;
            Nobility = population?.Nobility;
            Serfs = population?.Serfs;
            Slaves = population?.Slaves;
            ArtistCraft = population?.ArtistCraft;
            Clir = population?.Clir;
            Freeman = population?.Freeman;
        }
    }
}
