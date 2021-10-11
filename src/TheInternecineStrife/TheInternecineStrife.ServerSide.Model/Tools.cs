using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TheInternecineStrife.ServerSide.Model
{
    class Tools
    {
        protected static int CalcDistance(int A, int B, int face)
        {
            return Math.Abs(A % face - B % face) + Math.Abs(A / face - B / face);
        }

        protected static int[] GetVecineIndexes(int center, int face, int range) 
        {
            List<int> indexes = new List<int>(range * range * face);
            switch (range)
            {
                case 0: break;
                case 1: indexes.AddRange(new int[] { 1, -face, -1, face }.Select(index => index + center)); break;
                case 2: indexes.AddRange(new int[] {
                    1, -face, -1, face,
                    1 - face, -face - 1, face - 1, face + 1,
                    2, -2 * face, -2, 2 * face
                }.Select(index => index + center)); break;
                default:
                    if (range > face / 2)
                    {
                        range = face / 2;
                    }
                    
                    for (var i = 0; i < face*face; i++)
                    {
                        if (CalcDistance(i, center, face) <= range)
                        {
                            indexes.Add(i);
                        }
                    }
                    indexes = indexes.Where(inx => inx > 0 && inx < face * face).ToList();
                    break;
            }
            return indexes.ToArray();
        }
    }
}
