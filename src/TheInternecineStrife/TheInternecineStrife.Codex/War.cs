using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TheInternecineStrife.ServerSide.Model.War;
using TheInternecineStrife.ServerSide.Model.War.Battle;

namespace TheInternecineStrife.Codex
{
    public struct Rect
    {
        public readonly float X_Left;
        public readonly float X_Right;
        public readonly float Y_Top;
        public readonly float Y_Bottom;
        public readonly float Width;
        public readonly float Height;
        public readonly float Squer;
        public Rect(float left, float top, float right, float bottom)
        {
            X_Left = left;
            Y_Top = top;
            X_Right = right;
            Y_Bottom = bottom;
            Width = Math.Abs(right - left);
            Height = Math.Abs(bottom - top);
            Squer = Width * Height;
            if (top < bottom)
            {
                Y_Top = bottom;
                Y_Bottom = top;
            }
            if (left > right)
            {
                X_Left = right;
                X_Right = left;
            }
        }

        /// <summary>
        /// Вычислить пересечение областей.
        /// </summary>
        /// <param name="side">Другая область</param>
        /// <returns>Пересечение или null</returns>
        public Rect? GetOverlay(Rect side)
        {
            if (side.X_Left >= X_Right || side.X_Right <= X_Left || side.Y_Bottom <= Y_Top || side.Y_Top >= Y_Bottom)
            {
                return null;
            }
            return new Rect(
                Math.Max(X_Left, side.X_Left),
                Math.Max(Y_Top, side.Y_Top),
                Math.Min(X_Right, side.X_Right),
                Math.Min(Y_Bottom, side.Y_Bottom)
            );
        }

        /// <summary>
        /// Сместить область на вектр (dX, dY).
        /// </summary>
        /// <param name="dx">Сдвиг по оси X</param>
        /// <param name="dy">Сдвиг по оси Y</param>
        /// <returns>Новая область</returns>
        public Rect MoveAt(float dx, float dy)
        {
            return new Rect(
                X_Left + dx,
                Y_Top + dy,
                X_Right + dx,
                Y_Bottom + dy
            );
        }
    }

    public class War
    {
        /* Моделирование обстрела. */

        /// <summary>
        /// Получить площадь, на которую будут падать стрелы. Зависит от дальнобойности оружия и степени усталости стрелков.
        /// </summary>
        /// <param name="rangers">Полк стрелков</param>
        /// <returns>Площадь, осыпаемая стрелами.</returns>
        public Rect CalcArrowedSquer(BattleFormation rangers, float heightRanger, float heightTarget)
        {
            var ranDist = rangers.DistanceToCenter;
            var view = (float)(rangers.V.Direction);
            var near = view * rangers.Range.Near;
            var far = view * rangers.Side.Class.GetRangeLimit(heightRanger - heightTarget, rangers.Energy);
            return new Rect(
                0, ranDist - view * rangers.Length + near,
                0 + rangers.Width, ranDist + far
            );
        }

        /// <summary>
        /// Получить как можно более плотную (маленькую) зону обстрела.
        /// Стрелки стараются обстреливать именно дивизию.
        /// </summary>
        /// <param name="rangers">Полк стрелков</param>
        /// <param name="targets">В какой полк целятся</param>
        /// <param name="heightRanger">Высота положения стрелков</param>
        /// <param name="heightTarget">На какой высоте находятся цели</param>
        /// <returns>Область, в которую стараются попасть</returns>
        public Rect? CalcTargetSquer(BattleFormation rangers, BattleFormation targets, float heightRanger, float heightTarget)
        {
            var arcWide = Math.Max(
                Math.Min(
                    Math.Abs(rangers.DistanceToCenter - targets.DistanceToCenter),
                    rangers.Side.Class.GetRangeLimit(heightRanger - heightTarget, rangers.Energy)
                ),
                rangers.Range.Near
            );
            if (arcWide < rangers.Range.Near || arcWide > rangers.Range.Far)
            {
                return null;
            }
            var ranDist = rangers.DistanceToCenter;
            var view = (float)(rangers.V.Direction);
            var near = Math.Min(rangers.Range.Near, arcWide);
            return new Rect(
                0, ranDist - view * rangers.Length + near,
                0 + rangers.Width, ranDist + arcWide + 0.1f
            );
        }

        /// <summary>
        /// Определить, сколько солдат попадают в область обстрела.
        /// </summary>
        /// <param name="arrowed">Зона обстрела</param>
        /// <param name="targets">Дивизия, которую проверяют на попадание в зону обстрела</param>
        /// <returns>Число солдат, в которых хотя бы теоретически могли попасть.</returns>
        public int CalcOverArrowedAmount(Rect arrowed, BattleFormation targets)
        {
            var view = (float)(targets.V.Direction);
            var ranDist = targets.DistanceToCenter;
            var between = Math.Abs(ranDist - targets.DistanceToCenter);
            var targetSquer = new Rect(0, ranDist, 0 + targets.Width, ranDist + view*targets.Length);
            var firedOverlay = targetSquer.GetOverlay(arrowed);
            if (!firedOverlay.HasValue)
            {
                return 0;
            }
            return (int)Math.Floor(targets.Soldiers * Math.Min(firedOverlay.Value.Squer / targetSquer.Squer, 1));
        }

        public float CalcArrowedDensity(BattleFormation rangers, Rect arrowed, BattleFormation targets, float heightRanger, float heightTarget)
        {
            var shootSquer = CalcArrowedSquer(rangers, heightRanger, heightTarget);
            var densityOfShoot = rangers.Soldiers * shootSquer.Squer / arrowed.Squer;
            return densityOfShoot / CalcOverArrowedAmount(arrowed, targets);
        }

        /* Битва. */
    }
}
