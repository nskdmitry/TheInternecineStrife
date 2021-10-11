using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace TheInternecineStrife.ServerSide.Model.Social
{
    public delegate Tuple<int, float> Distributor(Stratum stratum, float gold);

    /// <summary>
    /// Население. Делится на сословия.
    /// </summary>
    public class Population
    {
        public Stratum Nobility = new Stratum(StratumClass.Classes[0]);
        public Stratum Merchantes = new Stratum(StratumClass.Classes[1]);
        public Stratum ArtistCraft = new Stratum(StratumClass.Classes[2]);
        public Stratum Clir = new Stratum(StratumClass.Classes[3]);
        public Stratum Freeman = new Stratum(StratumClass.Classes[4]);
        public Stratum Serfs = new Stratum(StratumClass.Classes[5]);
        public Stratum Slaves = new Stratum(StratumClass.Classes[6]);

        public int Men { get { return Nobility.Man + Merchantes.Man + ArtistCraft.Man + Clir.Man + Freeman.Man + Serfs.Man; } }
        public int Femen { get { return Nobility.Feman + Merchantes.Feman + ArtistCraft.Feman + Clir.Feman + Freeman.Feman + Serfs.Feman; } }
        public int Childrens
        {
            get
            {
                return Nobility.Kids + Merchantes.Kids + ArtistCraft.Kids + Clir.Kids + Freeman.Kids;
            }
        }

        /// <summary>
        /// Распределение доходов/убытков между сословиями.
        /// </summary>
        /// <param name="golds">Доход</param>
        /// TODO Возвращать должна список новых дивизий наемников.
        public void DistributionFunds(float golds)
        {
            Distributor destributer = (Stratum stratum, float gold) =>
            {
                var amountNow = (int)(Math.Min(stratum.Man, Math.Floor(golds / stratum.Class.Expenses)));
                var declassed = stratum.Man - amountNow;
                gold -= amountNow * stratum.Class.Expenses;
                stratum.Man = amountNow;
                return new Tuple<int, float>(declassed, gold);
            };
            var nobily = destributer(Nobility, golds);
            var merch = destributer(Merchantes, nobily.Item2);
            var craft = destributer(ArtistCraft, merch.Item2);
            var doctors = destributer(Clir, craft.Item2);
            var frees = destributer(Freeman, doctors.Item2);
            var serfs = destributer(Serfs, frees.Item2);
            destributer(Slaves, serfs.Item2);

            // Деклассирование разорившихся элементов.
            var toFree = nobily.Item1 + merch.Item1 + craft.Item1 + doctors.Item1;
            Freeman.Man += toFree;
            Freeman.Feman += toFree;
            Freeman.Kids += (int)Math.Max(toFree, Nobility.Kids + Merchantes.Kids + ArtistCraft.Kids + Clir.Kids - toFree);

            Slaves.Man += serfs.Item1;
            Slaves.Feman += serfs.Item1;
            Slaves.Kids += Math.Max(serfs.Item1, Serfs.Kids - serfs.Item1);
        }

        /// <summary>
        /// Рспределение трупов по сословиям. Чем меньше доля сословия, тем меньше у них смертей.
        /// </summary>
        /// <param name="man">Сколько умерло мужчин.</param>
        /// <param name="feman">Сколько умерло женщин.</param>
        /// <param name="kids">Сколько умерло детей.</param>
        public void Death(int man, int feman, int kids)
        {
            var all = Men;
            float nobilyProportion = Nobility.Man / all;
            float traderProportion = Merchantes.Man / all;
            float atisanProportion = ArtistCraft.Man / all;
            float clirProportion   = Clir.Man / all;
            float freesProportion  = Freeman.Man / all;
            float servesProportion = Serfs.Man / all;
            float slavesProportion = Slaves.Man / all;

            Nobility.Man = Math.Max(0, Nobility.Man - (int)(man * nobilyProportion));
            Merchantes.Man = Math.Max(0, Merchantes.Man - (int)(man * traderProportion));
            ArtistCraft.Man = Math.Max(0, ArtistCraft.Man - (int)(man * atisanProportion));
            Clir.Man = Math.Max(0, Clir.Man - (int)(man * clirProportion));
            Freeman.Man = Math.Max(0, Freeman.Man - (int)(man * freesProportion));
            Serfs.Man = Math.Max(0, Serfs.Man - (int)(man * servesProportion));
            Slaves.Man = Math.Max(0, Slaves.Man - (int)(man * slavesProportion));

            all = Femen;
            nobilyProportion = Nobility.Feman / all;
            traderProportion = Merchantes.Feman / all;
            atisanProportion = ArtistCraft.Feman / all;
            clirProportion = Clir.Feman / all;
            freesProportion = Freeman.Feman / all;
            servesProportion = Serfs.Feman / all;
            slavesProportion = Slaves.Feman / all;

            Nobility.Feman = Math.Max(0, Nobility.Feman - (int)(feman * nobilyProportion));
            Merchantes.Feman = Math.Max(0, Merchantes.Feman - (int)(feman * traderProportion));
            ArtistCraft.Feman = Math.Max(0, ArtistCraft.Feman - (int)(feman * atisanProportion));
            Clir.Feman = Math.Max(0, Clir.Feman - (int)(feman * clirProportion));
            Freeman.Feman = Math.Max(0, Freeman.Feman - (int)(feman * freesProportion));
            Serfs.Feman = Math.Max(0, Serfs.Feman - (int)(feman * servesProportion));
            Slaves.Feman = Math.Max(0, Slaves.Feman - (int)(feman * slavesProportion));

            all = kids;
            nobilyProportion = Nobility.Kids / all;
            traderProportion = Merchantes.Kids / all;
            atisanProportion = ArtistCraft.Kids / all;
            clirProportion = Clir.Kids / all;
            freesProportion = Freeman.Kids / all;
            servesProportion = Serfs.Kids / all;
            slavesProportion = Slaves.Kids / all;

            Nobility.Kids = Math.Max(0, Nobility.Kids - (int)(kids * nobilyProportion));
            Merchantes.Kids = Math.Max(0, Merchantes.Kids - (int)(kids * traderProportion));
            ArtistCraft.Kids = Math.Max(0, ArtistCraft.Kids - (int)(kids * atisanProportion));
            Clir.Kids = Math.Max(0, Clir.Kids - (int)(kids * clirProportion));
            Freeman.Kids = Math.Max(0, Freeman.Kids - (int)(kids * freesProportion));
            Serfs.Kids = Math.Max(0, Serfs.Kids - (int)(kids * servesProportion));
            Slaves.Kids = Math.Max(0, Slaves.Kids - (int)(kids * slavesProportion));
        }
    }
}
