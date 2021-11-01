using TheInternecineStrife.ServerSide.Model;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.Online.Models
{
    public class Regiment : Division
    {
        public Regiment(string title, int gameDay, Cell coordinator, SoldierProfile warclass, bool regular = false) 
            : base(title, gameDay, coordinator, warclass, regular)
        {
        }

        public Regiment(Division division) : 
            base(division.Name, division.NextPayDay, division.Sender, division.Profile, division.Regular)
        {
            Strength = division.Strength;
            Owner = division.Owner;
            Energy = division.Energy;
        }
    }
}
