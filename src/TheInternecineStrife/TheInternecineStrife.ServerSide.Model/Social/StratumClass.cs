using System.Collections.Generic;
using TheInternecineStrife.ServerSide.Model.War;

namespace TheInternecineStrife.ServerSide.Model.Social
{
    /// <summary>
    /// Сословие - группа людей по правам, доходу, возможностям и обязанностям.
    /// Сословие отвечает за функцию и то, кого можно призвать в качестве ополчения.
    /// </summary>
    public class StratumClass
    {
        public readonly int Id;
        public readonly string Name;
        public readonly bool Taxable;
        public readonly float Expenses;
        /// <summary>
        /// Как воружается сословное ополчение.
        /// </summary>
        public Dictionary<Age, SoldierProfile> MilitaryClasses;
        /// <summary>
        /// Гражданская функция сословия.
        /// </summary>
        public StratumProduction Production;
        /// <summary>
        /// Если сословие не служит, то как оно ему помогает?
        /// </summary>
        public RecruitToMilitary CallToMilitary;
        
        private StratumClass(int id, string name, bool tax, float expenseForLife = 1.0f)
        {
            Id = id;
            Name = name;
            Taxable = tax;
            Expenses = expenseForLife;
        }

        public static StratumClass[] Classes = new StratumClass[]
        {
            new StratumClass(0, "знать", false, 20) { MilitaryClasses = new Dictionary<Age, SoldierProfile> {
                {Age.StoneAge, SoldierProfile.Basic[1] },
                {Age.Neolit, SoldierProfile.Basic[8] },
                {Age.Bronze, SoldierProfile.Basic[15] },
                {Age.IronAge, SoldierProfile.Basic[22] },
                {Age.MiddleAge, SoldierProfile.Basic[29] }
            },
                // Ни хера не производят.
                Production = (Stratum group, Cell place) => { }
            },
            new StratumClass(1, "купцы", true, 10) { MilitaryClasses = new Dictionary<Age, SoldierProfile>
            {
                {Age.StoneAge, SoldierProfile.Basic[2] },
                {Age.Neolit, SoldierProfile.Basic[9] },
                {Age.Bronze, SoldierProfile.Basic[16] },
                {Age.IronAge, SoldierProfile.Basic[23] },
                {Age.MiddleAge, SoldierProfile.Basic[30] }
            },
                // Купцы приносят золото в карманы жителей поселка (свои, конечно же).
                Production = (Stratum group, Cell place) => { place.Settling.Founds = place.Settling.Founds * (1 + group.Man / 100); }
            },
            new StratumClass(2, "ремесленники", true, 8) { MilitaryClasses = new Dictionary<Age, SoldierProfile>
                {
                    {Age.StoneAge, SoldierProfile.Basic[3] },
                    {Age.Neolit, SoldierProfile.Basic[10] },
                    {Age.Bronze, SoldierProfile.Basic[17] },
                    {Age.IronAge, SoldierProfile.Basic[24] },
                    {Age.MiddleAge, SoldierProfile.Basic[31] }
                },
                // Ремесленники выполняют заказы на снаряжение войск. Нет заказа - нет работы.
                Production = (Stratum group, Cell place) => {
                    var order = group.CurrentOrder;
                    if (order == null || order.Left == 0)
                    {
                        return;
                    }
                }
            },
            new StratumClass(3, "врачи", false, 25) {
                // Врачи сокращают смертность при эпидемии.
                Production = (Stratum group, Cell place) => {
                    
                },
                // Врачи пополняют медбригады 
                CallToMilitary = (Stratum group, Army military) => { }
            },
            new StratumClass(4, "свободные", true, 0.5f) {
                // Свободные крестьяне и мещане вооружатся, чем могут
                MilitaryClasses = new Dictionary<Age, SoldierProfile> {

                },
                // Зарабатывают деньги и платят налоги
                Production = (Stratum group, Cell place) => { }
            },
            new StratumClass(5, "крепостные", true, 0.01f) {
                MilitaryClasses = new Dictionary<Age, SoldierProfile>
                {

                },
                Production = (Stratum group, Cell place) => { }
            },
            new StratumClass(6, "рабы", false, 0)
            {
            }
        };
    }
}
