using System;
using System.Collections.Generic;
using System.Threading;

namespace TheInternecineStrife.ServerSide.Model.War.Battle
{
  public struct StrikeResult
  {
    public int Attacks; // Сколько атаковало. Должно быть не больше суммы остальных полей.
    public int Killed; // Скольких убили
    public int Shallowed; // Легкораненых
    public int Wounded; // Серьезно раненых
    public int Heavyed; // При смерти
  }

  public class Batalia
  {
    public Cell Battleground;
    public BattleFormation Left;
    public BattleFormation Right;
    //public BattleCodex Rules { get; }
    public int Times { get; set; } // Notified

    private static Random Doom = new Random();

    public class Diapazone
    {
      public float Left = 0;
      public float Right = 0;
      public float Length { get { return Math.Abs(Right - Left); } }

      public void Check()
      {
        if (Left <= Right) {
          return;
        }

        var t = Left;
        Left = Right;
        Right = t;
      }

      public Diapazone GetPartition(Diapazone shorty)
      {
        Check();
        shorty.Check();
        if ((Left > shorty.Right && Left > shorty.Left) && (Right > shorty.Right && Right > shorty.Left)) {
          return null;
        }

        var coords = (new List<float>{ Left, Right, shorty.Left, shorty.Right });
        coords.Sort();
        return new Diapazone
        {
          Left = coords[1],
          Right = coords[2],
        };
      }
    }

    private StrikeResult rangeFire(bool fromLeft)
    {
      var view = fromLeft ? 1 : -1;
      var attacker = fromLeft ? Left : Right;
      var target = fromLeft ? Right : Left;
      var between = Math.Abs(target.DistanceToCenter - attacker.DistanceToCenter);
      InAttackRange(attacker, target, attacker.Range, attacker.RangeAttackDistance);
      if (attacker.RangeResource < 1) {
        throw new AttackBreaker("Has not catriges");
      }

      var overMax = new Diapazone()
      {
        Left = Math.Abs(attacker.DistanceToCenter - attacker.Columns * attacker.Density / attacker.Density + attacker.Range.Near) * view,
        Right = Math.Abs(attacker.DistanceToCenter + attacker.Range.Far) * view
      };
      var asTarget = overMax.GetPartition(new Diapazone() {
          Left =target.DistanceToCenter,
          Right =target.DistanceToCenter + target.Columns * target.Density / target.Density
      });
      // overed - в скольких могли попасть
      var deep = asTarget.Length;
      var fired = deep * attacker.Density * attacker.Columns;
      var overed = Math.Min(deep * target.Density * target.Columns, fired);

      // Koefficients: нормальное распределение, плотность огня, серьезность ран
      var bellCurveGoal = Math.Max(1.0 - Math.Sqrt(2 * between/(attacker.Range.Far - attacker.Range.Near)), 0.0001);
      var firefallKoeff = (fired / overed) * (attacker.Density / target.Density);
      var damageWound = attacker.Range.Damage / (target.Class == null ? target.Class.Health : 10);

      attacker.RangeResource--;
      // Единичные попадания
      var goaled = Doom.Next((int)Math.Min(bellCurveGoal * firefallKoeff * fired, fired), (int)fired);
      var weaponed = Doom.Next((int)((1.0 - bellCurveGoal) * overed), (int)overed);
      var onlyOnce = Doom.Next((int)((1.0 - bellCurveGoal) * weaponed), (int)weaponed);
      var damagePerHuman = damageWound * (goaled - onlyOnce) / (weaponed - onlyOnce);
      var result = new StrikeResult();
      result.Attacks = (int)fired;
      if (damageWound < 0.34) {
        result.Shallowed = onlyOnce;
      } else if (damageWound < 0.67) {
        result.Wounded = onlyOnce;
      } else if (damageWound < 0.96) {
        result.Heavyed = onlyOnce;
      } else {
        result.Killed = onlyOnce;
      }
      goaled -= onlyOnce;
      weaponed -= onlyOnce;

      var curve = 1.0;
      var k = Math.Min(0.0, curve - bellCurveGoal / 2);
      var wounded = (int)Math.Ceiling(k *  weaponed);
      result.Killed += wounded;
      weaponed -= wounded;
      curve -= k;

      k = (1 - curve) / curve;
      wounded = (int)Math.Ceiling(k * weaponed);
      result.Shallowed += wounded;
      result.Heavyed += wounded;
      weaponed = wounded;
      result.Wounded += weaponed;

      return result;
    }

    private StrikeResult linearMalee(bool fromLeft)
    {
        var attacker = fromLeft ? Left : Right;
        var target = fromLeft ? Right : Left;
        var toFirstRow = Math.Abs(target.DistanceToCenter - attacker.DistanceToCenter);
        InAttackRange(attacker, target, attacker.Malee, attacker.MaleeAttackDistance);
        return new StrikeResult { };
    }

    private bool InAttackRange(BattleFormation attacker, BattleFormation target, Weapon tool, float attackDistance)
    {
      var toFirstRow = Math.Abs(target.DistanceToCenter - attacker.DistanceToCenter);
      if (toFirstRow > tool.Far || toFirstRow + attacker.Length + target.Length < tool.Near) {
        throw new AttackBreaker("Out of range bounds");
      }
      if (attacker.RangeResource < 1) {
        throw new AttackBreaker("The shells are exhausted");
      }
      // TODO Учесть размеры строя лучников и целевого строя
      if (attackDistance < toFirstRow)
      {
        throw new AttackBreaker("Very early");
      }

      return true;
    }
  }
}
