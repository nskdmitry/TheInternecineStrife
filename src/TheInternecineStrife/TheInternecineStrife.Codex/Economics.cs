using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TheInternecineStrife.ServerSide.Model;
using TheInternecineStrife.ServerSide.Model.Economic;

namespace TheInternecineStrife.Codex
{
    public class Economics
    {
        public List<Good> TypesOfGoods = new List<Good>(20);
        const float SQUER_KOEF = 100;
        const float EARTH_MATERIAL_KOEF = 1.2f;
        const float AGE_BUILDING_PRICE = 200f;

        /// <summary>Подсчет стоимости возведения/наращивания стен. Используется, в том числе, и для определения стоимости ремонта. </summary>
        /// <param name="current">Текущее состояние стен.</param>
        /// <param name="goal">Желательное состояние стен.</param>
        /// <returns>Стоимость в золоте данных работ без учета уже имеющегося материала.</returns>
        float CalcBuildingWallsCost(WallOptions current, WallOptions goal)
        {
            if (goal.Material.Id != current.Material.Id)
            {
                // Замена стен означает снос имеющихся. А это - отдельная статья расходов.
                var laborIntensityDestruct = current.Material.Density * current.Material.Density * Math.Sqrt(current.Height);
                var laborIntensityBuild = goal.Material.Density * goal.Material.Density * Math.Sqrt(goal.Height);
                var destructionCost = current.Volume * laborIntensityDestruct;
                var buildCost = goal.Volume * laborIntensityBuild * goal.Material.Type.Price;
                return (float)(destructionCost + buildCost);
            }

            var material = goal.Material;
            var laborIntensity = material.Density * material.Density * Math.Sqrt(current.Height);
            var repairs = current.RepairVolume;
            var growValue = Math.Abs(goal.Height - current.Height);
            return (float)(laborIntensity * (growValue + repairs) * material.Type.Price);
        }

        /// <summary>
        /// Подсчет стоимости ручного увеличения высоты клетки. Для чего это может быть нужно?
        /// 1) Чем выше клетка относительно соседей, тем дальше могут стрелять с неё стрелки, и тем ближе надо подходить врагам.
        /// 2) Высоты стен и клетки складываются для защитников. Стены - дороги и требуют ремонта, тогда как курган - разовая работа.
        /// 3) Подняв клетку до минимальной нужной высоты, можно будет терраформировать её в новый, более выгодный, тип ландшафта.
        /// </summary>
        /// <param name="cell">Клетка, для которой проводяся расчеты.</param>
        /// <param name="goalHeight">Поднять до какой высоты?</param>
        /// <returns>ВО сколько это обойдется</returns>
        float CalcCellUplandingCost(Cell cell, float goalHeight)
        {
            var laborIntensity = Math.Sqrt(cell.Height * (goalHeight - cell.Height) * SQUER_KOEF);
            return (float)(EARTH_MATERIAL_KOEF * laborIntensity);
        }

        /// <summary>
        /// Стоимость возведения нового поселения. Складывается из требований к домам + стоимости цен.
        /// </summary>
        /// <param name="dwelling">Тип поселения.</param>
        /// <param name="walls">Параметры стен</param>
        /// <exception cref="InvalidOperationException">
        /// 1) Поселение уже основано в этой клетке.
        /// 2) Ландшафт несовместим с типом поселения.
        /// 3) Указан тип ландшфта, не являющийся антропогенным.
        /// </exception>
        /// <returns>Итоговая стоимость.</returns>
        float CalcSettlingCost(Cell place, LandType dwelling, WallOptions walls)
        {
            if (place.Settling != null)
            {
                throw new InvalidOperationException("Уже основано.");
            }
            if (place.Background.Envirounment != dwelling.Envirounment)
            {
                throw new InvalidOperationException("Ландшафт несовместим с типом поселения.");
            }
            if (!dwelling.Civilization)
            {
                throw new InvalidOperationException("Это не вид поселения.");
            }

            var ageKoeff = (int)dwelling.Level - (int)Age.Neolit;
            var buildCost = CalcBuildingWallsCost(WallOptions.None, walls);
            return ageKoeff * AGE_BUILDING_PRICE + buildCost;
        }


    }
}
