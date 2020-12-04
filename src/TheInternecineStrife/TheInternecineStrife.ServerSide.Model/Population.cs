using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace TheInternecineStrife.ServerSide.Model
{
    public class Population
    {
        public int Men { get; set; }
        public int Femen { get; set; }
        public int Childrens { get; set; }
        
        #region Operators
        public static Population operator +(Population receiver, Population sender)
        {
            return new Population() {
                Men = receiver.Men + sender.Men,
                Femen = receiver.Femen + sender.Femen,
                Childrens = receiver.Childrens + sender.Childrens
            };
        }

        public static Population operator -(Population sender, Population receiver)
        {
            return new Population()
            {
                Men = receiver.Men - sender.Men,
                Femen = receiver.Femen - sender.Femen,
                Childrens = receiver.Childrens - sender.Childrens
            };
        }
        #endregion
    }
}
