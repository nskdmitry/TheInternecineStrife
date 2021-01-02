using System;

namespace TheInternecineStrife.ServerSide.Model.War.Battle
{
    public class AttackBreaker : Exception
    {
        public AttackBreaker(string message) : base(message)
        {
            
        }
    }
}
