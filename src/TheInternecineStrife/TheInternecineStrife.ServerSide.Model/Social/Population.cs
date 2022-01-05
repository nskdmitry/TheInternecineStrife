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

        public int Men {
            get { return Nobility.Man + Merchantes.Man + ArtistCraft.Man + Clir.Man + Freeman.Man + Serfs.Man; }
        }
        public int Femen {
            get { return Nobility.Feman + Merchantes.Feman + ArtistCraft.Feman + Clir.Feman + Freeman.Feman + Serfs.Feman; }
        }
        public int Childrens
        {
            get
            {
                return Nobility.Kids + Merchantes.Kids + ArtistCraft.Kids + Clir.Kids + Freeman.Kids + Serfs.Kids;
            }
        }
        public int People { get => Men + Femen; }

        /// <summary>
        /// Распределение доходов/убытков между сословиями.
        /// </summary>
        /// <param name="golds">Доход</param>
        /// TODO Возвращать должна список новых дивизий наемников.
        public void DistributionFunds(float golds)
        {
            var nobily = DistributeIncomeBetweenStratums(Nobility, golds);
            var merch = DistributeIncomeBetweenStratums(Merchantes, nobily.Item2);
            var craft = DistributeIncomeBetweenStratums(ArtistCraft, merch.Item2);
            var doctors = DistributeIncomeBetweenStratums(Clir, craft.Item2);
            var frees = DistributeIncomeBetweenStratums(Freeman, doctors.Item2);
            var serfs = DistributeIncomeBetweenStratums(Serfs, frees.Item2);
            DistributeIncomeBetweenStratums(Slaves, serfs.Item2);

            // Деклассирование разорившихся элементов.
            var toFree = nobily.Item1 + merch.Item1 + craft.Item1 + doctors.Item1;
            Freeman.Man += toFree;
            Freeman.Feman += toFree;
            Freeman.Kids += (int)Math.Max(toFree, Nobility.Kids + Merchantes.Kids + ArtistCraft.Kids + Clir.Kids - toFree);

            Slaves.Man += serfs.Item1;
            Slaves.Feman += serfs.Item1;
            Slaves.Kids += Math.Max(serfs.Item1, Serfs.Kids - serfs.Item1);
        }

        public void Death(int man, int feman, int kids)
        {
            CountAlivedMan(man);
            CountAlivedWoman(feman);
            CountAlivedKids(kids);
        }

        private void CountAlivedMan(int lost)
        {
            var all = Men;
            Nobility.Man = CountAlived(Nobility.Man, all, lost);
            Clir.Man = CountAlived(Clir.Man, all, lost);
            Merchantes.Man = CountAlived(Merchantes.Man, all, lost);
            ArtistCraft.Man = CountAlived(ArtistCraft.Man, all, lost);
            Freeman.Man = CountAlived(Freeman.Man, all, lost);
            Serfs.Man = CountAlived(Serfs.Man, all, lost);
            Slaves.Man = CountAlived(Slaves.Man, all, lost);
        }

        private void CountAlivedWoman(int lost)
        {
            var all = Femen;
            Nobility.Feman = CountAlived(Nobility.Feman, all, lost);
            Clir.Feman = CountAlived(Clir.Feman, all, lost);
            Merchantes.Feman = CountAlived(Merchantes.Feman, all, lost);
            ArtistCraft.Feman = CountAlived(ArtistCraft.Feman, all, lost);
            Freeman.Feman = CountAlived(Freeman.Feman, all, lost);
            Serfs.Feman = CountAlived(Serfs.Feman, all, lost);
            Slaves.Feman = CountAlived(Slaves.Feman, all, lost);
        }

        private void CountAlivedKids(int lost)
        {
            var all = Childrens;
            Nobility.Kids = CountAlived(Nobility.Kids, all, lost);
            Merchantes.Kids = CountAlived(Merchantes.Kids, all, lost);
            ArtistCraft.Kids = CountAlived(ArtistCraft.Kids, all, lost);
            Clir.Kids = CountAlived(Clir.Kids, all, lost);
            Freeman.Kids = CountAlived(Freeman.Kids, all, lost);
            Serfs.Kids = CountAlived(Serfs.Kids, all, lost);
            Slaves.Kids = CountAlived(Slaves.Kids, all, lost);
        }

        private int CountAlived(int stratumPeople, int allPeople, int dieds)
        {
            float proportion = stratumPeople / allPeople;
            return Math.Max(0, Nobility.Man - (int)(dieds * proportion));
        }

        private readonly Distributor DistributeIncomeBetweenStratums = (Stratum stratum, float gold) =>
        {
            var amountNow = (int)(Math.Min(stratum.Man, Math.Floor(gold / stratum.Class.Expenses)));
            var declassed = stratum.Man - amountNow;
            gold -= amountNow * stratum.Class.Expenses;
            stratum.Man = amountNow;
            return new Tuple<int, float>(declassed, gold);
        };
    }
}
